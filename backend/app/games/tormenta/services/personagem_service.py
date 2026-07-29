"""Regras de negócio — personagens Tormenta 20."""

from __future__ import annotations

from typing import List, Optional

from app.games.tormenta.models.campanha import TormentaCampanha
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.ports import TormentaPersonagemRepositoryProtocol
from app.games.tormenta.rules.ameaca_bloco_t20 import (
    consolidar_ameaca_de_personagem,
    limpar_texto_override,
    montar_bloco_ameaca,
    obter_nd,
    obter_papel_combate,
)
from app.games.tormenta.rules.atributos_t20 import (
    METODO_GERACAO_PADRAO,
    custo_total_compra_seis_atributos,
    normalizar_metodo_geracao_atributos,
    pontos_iniciais_compra,
    validar_valores_base_4d6,
)
from app.games.tormenta.rules.bestiario_import_t20 import criar_payload_import_bestiario
from app.games.tormenta.rules.classes_t20 import validar_compatibilidade_classes_v13
from app.games.tormenta.rules.conjuracao_t20 import (
    classe_conjuracao_mb_registrada,
    pontos_magia_maximos_conjuracao,
)
from app.games.tormenta.rules.defesa_t20 import defesa_base_ca
from app.games.tormenta.rules.duende_t20 import validar_duende_ficha
from app.games.tormenta.rules.melhor_amigo_t20 import validar_melhor_amigo_ficha
from app.games.tormenta.rules.origens_t20 import (
    habilidade_ativa_origem,
    normalizar_beneficios_origem,
    origem_tem_beneficio_fixo,
    sincronizar_pericias_origem_ficha_json,
    validar_beneficios_origem,
    validar_trocas_pericia_origem,
)
from app.games.tormenta.rules.pericias_criacao_t20 import validar_pericias_ficha
from app.games.tormenta.rules.progressao_pv_t20 import (
    niveis_multiclasse_v13_de_ficha,
    preview_pm_multiclasse_v13,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)
from app.games.tormenta.rules.tendencias_divindades_t20 import validar_devocao_v13
from app.games.tormenta.schemas.habilidade_origem import (
    TormentaHabilidadeOrigemAtivarResponse,
)
from app.games.tormenta.schemas.personagem import (
    TormentaBestiarioImportRequest,
    TormentaBlocoAmeacaResponse,
    TormentaConverterAmeacaRequest,
    TormentaPersonagemCreate,
    TormentaPersonagemResponse,
    TormentaPersonagemUpdate,
)
from app.games.tormenta.services.personagem_equipamentos_service import (
    TormentaPersonagemEquipamentosService,
)
from app.games.tormenta.services.personagem_talentos_service import (
    TormentaPersonagemTalentosService,
)
from app.repositories.base import commit_with_rollback
from app.shared.core.usuario_lookup import enriquecer_dono_nome_em_entidades
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import PerfilUsuario, Usuario


class TormentaPersonagemService:
    _CHAVES_COMPRA = ("for", "des", "con", "int", "sab", "car")
    _CAMPOS_ATRIBUTO = (
        "for_valor",
        "des_valor",
        "con_valor",
        "int_valor",
        "sab_valor",
        "car_valor",
    )

    @staticmethod
    def _patch_mexe_compra_pontos(data: dict) -> bool:
        """True se o PATCH altera atributos, método de geração ou atributos_compra."""
        if any(
            k in data for k in ("tipo",) + TormentaPersonagemService._CAMPOS_ATRIBUTO
        ):
            return True
        fj = data.get("ficha_json")
        if not isinstance(fj, dict):
            return False
        return "atributos_compra" in fj or "metodo_geracao_atributos" in fj

    @staticmethod
    def _patch_mexe_pericias_mb(data: dict) -> bool:
        """True se o PATCH altera nível, INT ou bloco de perícias/classe MB."""
        if any(k in data for k in ("tipo", "nivel", "int_valor")):
            return True
        fj = data.get("ficha_json")
        if not isinstance(fj, dict):
            return False
        return bool(
            fj.keys() & {"pericias", "tormenta_classe_mb_slug", "raca_tormenta_slug"}
        )

    def __init__(self, repo: TormentaPersonagemRepositoryProtocol):
        self.repo = repo

    @staticmethod
    def _tipos_validos() -> set:
        return {"jogador", "monstro", "npc"}

    def _usuario_pode_mestrar_tormenta(self, usuario: Usuario) -> bool:
        if usuario.perfil in (
            PerfilUsuario.ADMINISTRADOR,
            PerfilUsuario.MESTRE,
        ):
            return True
        row = (
            self.repo.db.query(TormentaCampanha.id)
            .filter(TormentaCampanha.mestre_id == usuario.id)
            .limit(1)
            .scalar()
        )
        return isinstance(row, int)

    @staticmethod
    def _usuario_e_admin(usuario: Usuario) -> bool:
        return usuario.perfil == PerfilUsuario.ADMINISTRADOR

    def _assert_mestre_da_campanha(self, usuario: Usuario, campanha_id: int) -> None:
        if self._usuario_e_admin(usuario):
            campanha = (
                self.repo.db.query(TormentaCampanha)
                .filter(TormentaCampanha.id == campanha_id)
                .first()
            )
        else:
            campanha = (
                self.repo.db.query(TormentaCampanha)
                .filter(
                    TormentaCampanha.id == campanha_id,
                    TormentaCampanha.mestre_id == usuario.id,
                )
                .first()
            )
        if not campanha:
            raise ArenaBaseException(
                "Campanha nao encontrada ou sem permissao", status_code=403
            )

    def _resolver_dono(self, usuario: Usuario, tipo: str) -> Optional[int]:
        t = (tipo or "").lower()
        if self._usuario_pode_mestrar_tormenta(usuario):
            if t in ("monstro", "npc"):
                return None
        return usuario.id

    @staticmethod
    def _nivel_conjuracao_mb_para_pm(
        ficha_json: Optional[dict], nivel_personagem: int
    ) -> int:
        fj = dict(ficha_json or {})
        raw = fj.get("tormenta_nivel_conjurador_mb")
        try:
            if raw is not None and str(raw).strip() != "":
                n = int(raw)
                return max(1, min(40, n))
        except (TypeError, ValueError):
            pass
        try:
            n = int(nivel_personagem)
            return max(1, min(40, n if n >= 1 else 1))
        except (TypeError, ValueError):
            return 1

    @classmethod
    def _pm_mb_calculado(
        cls,
        ficha_json: Optional[dict],
        nivel_personagem: int,
        fv: int,
        dv: int,
        cv: int,
        iv: int,
        sv: int,
        carv: int,
    ) -> Optional[int]:
        fj = dict(ficha_json or {})
        slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        if not slug:
            return None
        rv = regra_versao_de_ficha(fj)
        if rv == REGRA_VERSAO_V13:
            linhas = niveis_multiclasse_v13_de_ficha(fj, int(nivel_personagem))
            if linhas:
                prev = preview_pm_multiclasse_v13(
                    linhas,
                    ficha_json=fj,
                    nivel_personagem=int(nivel_personagem),
                )
                pm = prev.get("pm_max")
                return int(pm) if pm is not None else None
        arcanista = str(fj.get("arcanista_caminho") or "").strip().lower() or None
        nv = (
            int(nivel_personagem)
            if rv == REGRA_VERSAO_V13
            else cls._nivel_conjuracao_mb_para_pm(fj, nivel_personagem)
        )
        return pontos_magia_maximos_conjuracao(
            slug,
            nv,
            fv,
            dv,
            cv,
            iv,
            sv,
            carv,
            regra_versao=rv,
            arcanista_caminho=arcanista,
        )

    @classmethod
    def _resolver_pa_magia_criacao(
        cls, payload: TormentaPersonagemCreate
    ) -> tuple[int, int]:
        pm = cls._pm_mb_calculado(
            payload.ficha_json,
            int(payload.nivel),
            int(payload.for_valor),
            int(payload.des_valor),
            int(payload.con_valor),
            int(payload.int_valor),
            int(payload.sab_valor),
            int(payload.car_valor),
        )
        if pm is not None:
            pa_max = max(0, min(999, int(pm)))
        else:
            pa_max = max(0, min(999, int(payload.pa_max)))
        pa_atual = payload.pa_atual if payload.pa_atual is not None else pa_max
        pa_atual = int(pa_atual)
        if pa_max:
            pa_atual = min(max(-999, pa_atual), pa_max)
        pa_atual = max(-999, min(999, pa_atual))
        return pa_max, pa_atual

    def _sincronizar_pontos_magia_mb(self, ent: TormentaPersonagem) -> None:
        """Recalcula PM máximos: v1.3 (todas as classes) ou MB (só conjuradores na tabela)."""
        fj = dict(ent.ficha_json or {})
        slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        if not slug:
            return
        rv = regra_versao_de_ficha(fj)
        if rv != REGRA_VERSAO_V13 and not classe_conjuracao_mb_registrada(slug):
            return
        pm = self._pm_mb_calculado(
            fj,
            int(ent.nivel),
            int(ent.for_valor),
            int(ent.des_valor),
            int(ent.con_valor),
            int(ent.int_valor),
            int(ent.sab_valor),
            int(ent.car_valor),
        )
        if pm is None:
            ent.pa_max = 0
            ent.pa_atual = 0
            return
        old_max = int(ent.pa_max or 0)
        new_max = max(0, min(999, int(pm)))
        ent.pa_max = new_max
        cur = int(ent.pa_atual) if ent.pa_atual is not None else new_max
        if new_max > old_max:
            cur = min(cur + (new_max - old_max), new_max)
        else:
            cur = min(cur, new_max)
        ent.pa_atual = min(max(0, cur), new_max)

    def _sincronizar_ca_v13(self, ent: TormentaPersonagem) -> None:
        """v1.3: CA base de jogador = 10 + DES; monstro/NPC mantém Defesa explícita (bestiário)."""
        if (ent.tipo or "").lower() != "jogador":
            return
        fj = dict(ent.ficha_json or {})
        if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
            return
        ent.ca = defesa_base_ca(int(ent.des_valor or 0), REGRA_VERSAO_V13)

    def _validar_tipo(self, tipo: str) -> None:
        if (tipo or "").lower() not in self._tipos_validos():
            raise DadosInvalidos("tipo deve ser jogador, monstro ou npc")

    @staticmethod
    def _seis_valores_compra_pontos(
        ficha_json: Optional[dict],
        for_valor: int,
        des_valor: int,
        con_valor: int,
        int_valor: int,
        sab_valor: int,
        car_valor: int,
    ) -> tuple[int, int, int, int, int, int]:
        """Usa ficha_json.atributos_compra quando completo; senão os seis atributos persistidos."""
        cols = (for_valor, des_valor, con_valor, int_valor, sab_valor, car_valor)
        if not ficha_json:
            return cols
        ac = ficha_json.get("atributos_compra")
        if not isinstance(ac, dict):
            return cols
        try:
            vals: list[int] = []
            for k in TormentaPersonagemService._CHAVES_COMPRA:
                if k not in ac:
                    return cols
                vals.append(int(ac[k]))
            return (vals[0], vals[1], vals[2], vals[3], vals[4], vals[5])
        except (TypeError, ValueError):
            return cols

    @staticmethod
    def _metodo_geracao_atributos(ficha_json: Optional[dict]) -> str:
        if not ficha_json:
            return METODO_GERACAO_PADRAO
        raw = ficha_json.get("metodo_geracao_atributos")
        try:
            return normalizar_metodo_geracao_atributos(
                str(raw) if raw is not None else METODO_GERACAO_PADRAO
            )
        except ValueError:
            return METODO_GERACAO_PADRAO

    @staticmethod
    def _validar_atributos_criacao_jogador(
        tipo: str,
        ficha_json: Optional[dict],
        for_valor: int,
        des_valor: int,
        con_valor: int,
        int_valor: int,
        sab_valor: int,
        car_valor: int,
    ) -> None:
        """Jogador: valida compra por pontos (20 pts) ou rolagem 4d6 conforme metodo_geracao_atributos."""
        if (tipo or "").lower() != "jogador":
            return
        rv = regra_versao_de_ficha(ficha_json)
        metodo = TormentaPersonagemService._metodo_geracao_atributos(ficha_json)
        fv, dv, cv, iv, sv, cav = TormentaPersonagemService._seis_valores_compra_pontos(
            ficha_json, for_valor, des_valor, con_valor, int_valor, sab_valor, car_valor
        )
        bases = (fv, dv, cv, iv, sv, cav)
        if metodo == "4d6":
            try:
                validar_valores_base_4d6(bases, rv)
            except ValueError as exc:
                raise DadosInvalidos(str(exc)) from exc
            return
        meta = pontos_iniciais_compra(rv)
        total = custo_total_compra_seis_atributos(fv, dv, cv, iv, sv, cav, rv)
        intervalo = "entre −2 e +4 (v1.3)" if rv == "v13" else "entre 8 e 18 (MB)"
        if total is None:
            raise DadosInvalidos(
                f"Ficha tipo jogador: cada valor em atributos_compra (ou atributo do personagem) "
                f"usado na soma deve estar {intervalo}."
            )
        if int(total) > int(meta):
            raise DadosInvalidos(
                f"Ficha tipo jogador: custo na compra por pontos nao pode ultrapassar {meta} "
                f"(gasto atual: {total}). Ajuste ficha_json.atributos_compra ou os seis atributos."
            )
        if int(total) < int(meta):
            edicao = "v1.3" if rv == "v13" else "MB"
            raise DadosInvalidos(
                f"Ficha tipo jogador: e obrigatorio gastar os {meta} pontos na compra por pontos do {edicao} "
                f"(gasto atual: {total}). Ajuste ficha_json.atributos_compra ou os seis atributos."
            )

    @staticmethod
    def _validar_pericias_t20_jogador(
        tipo: str,
        ficha_json: Optional[dict],
        nivel: int,
        int_valor: int,
        *,
        criacao: bool = False,
    ) -> None:
        """Jogador com classe MB: valida vagas treinadas e graduações de perícias."""
        if (tipo or "").lower() != "jogador":
            return
        if not ficha_json:
            return
        wizard_v13 = bool(ficha_json.get("pericias_wizard_v13"))
        cadastro_dash = bool(ficha_json.get("cadastro_dashboard"))
        if criacao and cadastro_dash and not wizard_v13:
            return
        slug = str(ficha_json.get("tormenta_classe_mb_slug") or "").strip().lower()
        if not slug:
            return
        pericias = ficha_json.get("pericias")
        if not isinstance(pericias, list) or len(pericias) == 0:
            if wizard_v13 or (criacao and cadastro_dash):
                raise DadosInvalidos(
                    "Orçamento de perícias: selecione perícias treinadas na criação."
                )
            return
        raca_slug = str(ficha_json.get("raca_tormenta_slug") or "").strip().lower()
        if raca_slug in ("__livre__", ""):
            raca_slug = None
        ok, motivo, _ = validar_pericias_ficha(
            nivel=int(nivel or 1),
            slug_classe=slug,
            int_valor=int(int_valor),
            slug_raca=raca_slug,
            pericias=pericias,
            regra_versao=regra_versao_de_ficha(ficha_json),
            humano_versatil=ficha_json.get("humano_versatil"),
            origem_beneficios=ficha_json.get("origem_beneficios"),
            origem_slug=str(ficha_json.get("origem_slug") or "").strip().lower()
            or None,
            origem_trocas_pericia=ficha_json.get("origem_trocas_pericia"),
        )
        if not ok:
            raise DadosInvalidos(motivo or "Orçamento de perícias MB inválido.")

    @staticmethod
    def _validar_arcanista_caminho_v13(tipo: str, ficha_json: Optional[dict]) -> None:
        if (tipo or "").lower() != "jogador":
            return
        if not ficha_json:
            return
        if regra_versao_de_ficha(ficha_json) != REGRA_VERSAO_V13:
            return
        slug = str(ficha_json.get("tormenta_classe_mb_slug") or "").strip().lower()
        if slug != "arcanista":
            return
        cam = str(ficha_json.get("arcanista_caminho") or "").strip().lower()
        if cam not in ("bruxo", "mago", "feiticeiro"):
            raise DadosInvalidos(
                "Arcanista v1.3: escolha o caminho Bruxo, Mago ou Feiticeiro (irreversível)."
            )

    @staticmethod
    def _validar_origem_v13(
        tipo: str, ficha_json: Optional[dict], *, criacao: bool = False
    ) -> None:
        if (tipo or "").lower() != "jogador":
            return
        fj = dict(ficha_json or {})
        if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
            return
        slug = str(fj.get("origem_slug") or "").strip().lower()
        if not slug:
            if criacao:
                raise DadosInvalidos(
                    "Ficha v1.3 tipo jogador: origem obrigatoria (ficha_json.origem_slug)."
                )
            return
        ben = fj.get("origem_beneficios")
        if not isinstance(ben, list):
            ben = []
        if origem_tem_beneficio_fixo(slug):
            # Origens de Heróis de Arton concedem tudo automaticamente; o cliente
            # só envia a escolha opcional de poder, quando houver.
            ben = normalizar_beneficios_origem(slug, ben)
            if isinstance(ficha_json, dict):
                ficha_json["origem_beneficios"] = list(ben)
        ok, motivo = validar_beneficios_origem(slug, ben)
        if not ok:
            raise DadosInvalidos(motivo or "Benefícios de origem inválidos.")
        cls = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        ok_troca, motivo_troca = validar_trocas_pericia_origem(
            slug,
            ben,
            fj.get("origem_trocas_pericia"),
            cls,
            fj.get("pericias"),
        )
        if not ok_troca:
            raise DadosInvalidos(motivo_troca or "Troca de perícia de origem inválida.")

    @staticmethod
    def _validar_devocao_v13(
        tipo: str,
        ficha_json: Optional[dict],
        *,
        divindade_rotulo: Optional[str] = None,
    ) -> None:
        if (tipo or "").lower() != "jogador":
            return
        fj = dict(ficha_json or {})
        if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
            return
        ok, motivo = validar_devocao_v13(fj, divindade_rotulo=divindade_rotulo)
        if not ok:
            raise DadosInvalidos(motivo or "Devoção inválida.")

    @staticmethod
    def _validar_classes_variantes_v13(
        tipo: str,
        ficha_json: Optional[dict],
        nivel: int,
    ) -> None:
        if (tipo or "").lower() != "jogador":
            return
        fj = dict(ficha_json or {})
        if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
            return
        err = validar_compatibilidade_classes_v13(fj, nivel)
        if err:
            raise DadosInvalidos(err)

    @staticmethod
    def _validar_melhor_amigo_v13(tipo: str, ficha_json: Optional[dict]) -> None:
        if (tipo or "").lower() != "jogador":
            return
        fj = dict(ficha_json or {})
        if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
            return
        if not fj.get("melhor_amigo"):
            return
        ok, motivo = validar_melhor_amigo_ficha(fj)
        if not ok:
            raise DadosInvalidos(motivo or "Melhor Amigo inválido.")

    @staticmethod
    def _validar_duende_v13(tipo: str, ficha_json: Optional[dict]) -> None:
        if (tipo or "").lower() != "jogador":
            return
        fj = dict(ficha_json or {})
        if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
            return
        slug = str(fj.get("raca_tormenta_slug") or "").strip().lower()
        if slug != "duende" and not fj.get("duende"):
            return
        ok, motivo = validar_duende_ficha(fj)
        if not ok:
            raise DadosInvalidos(motivo or "Duende inválido.")

    @staticmethod
    def _preparar_ficha_json_tormenta(ficha_json: Optional[dict]) -> dict:
        """Normaliza ficha_json v1.3 (ex.: perícias treinadas pela origem)."""
        fj = dict(ficha_json or {})
        if regra_versao_de_ficha(fj) == REGRA_VERSAO_V13:
            fj = sincronizar_pericias_origem_ficha_json(fj)
        return fj

    def _sincronizar_poderes_v13(self, personagem_id: int, ficha_json: dict) -> None:
        if regra_versao_de_ficha(ficha_json) != REGRA_VERSAO_V13:
            return
        TormentaPersonagemTalentosService(
            self.repo.db
        ).sincronizar_poderes_automaticos_v13(personagem_id, ficha_json)

    def _sincronizar_equipamentos_v13(
        self, personagem_id: int, ficha_json: dict, nivel: int
    ) -> None:
        if regra_versao_de_ficha(ficha_json) != REGRA_VERSAO_V13:
            return
        fj = dict(ficha_json or {})
        fj["nivel"] = int(nivel or 1)
        TormentaPersonagemEquipamentosService(
            self.repo.db
        ).sincronizar_equipamentos_automaticos_v13(personagem_id, fj)

    def _para_resposta(self, ent: TormentaPersonagem) -> TormentaPersonagemResponse:
        enriquecer_dono_nome_em_entidades(self.repo.db, [ent])
        return TormentaPersonagemResponse.model_validate(ent)

    def _para_respostas(
        self, rows: List[TormentaPersonagem]
    ) -> List[TormentaPersonagemResponse]:
        enriquecer_dono_nome_em_entidades(self.repo.db, rows)
        return [TormentaPersonagemResponse.model_validate(r) for r in rows]

    def listar_todos(
        self,
        tipo: Optional[str],
        *,
        usuario: Usuario,
        skip: int = 0,
        limit: int = 100,
        apenas_meus: bool = False,
        campanha_id: Optional[int] = None,
    ) -> List[TormentaPersonagemResponse]:
        if campanha_id is not None:
            self._assert_mestre_da_campanha(usuario, campanha_id)
            if tipo:
                rows = self.repo.get_by_campanha(
                    campanha_id, tipo, skip=skip, limit=limit
                )
            else:
                rows = self.repo.get_by_campanha(campanha_id, skip=skip, limit=limit)
            return self._para_respostas(rows)

        if not self._usuario_e_admin(usuario):
            if tipo:
                rows = self.repo.get_by_owner_and_tipo(
                    usuario.id, tipo, skip=skip, limit=limit
                )
            else:
                rows = self.repo.get_by_owner(usuario.id, skip=skip, limit=limit)
            return self._para_respostas(rows)

        if apenas_meus:
            if tipo:
                rows = self.repo.get_by_owner_and_tipo(
                    usuario.id, tipo, skip=skip, limit=limit
                )
            else:
                rows = self.repo.get_by_owner(usuario.id, skip=skip, limit=limit)
            return self._para_respostas(rows)

        if tipo:
            rows = self.repo.get_by_tipo(tipo, skip=skip, limit=limit)
        else:
            rows = self.repo.get_all(skip=skip, limit=limit)
        return self._para_respostas(rows)

    def contar_todos(
        self,
        tipo: Optional[str],
        *,
        usuario: Usuario,
        apenas_meus: bool = False,
        campanha_id: Optional[int] = None,
    ) -> int:
        if campanha_id is not None:
            self._assert_mestre_da_campanha(usuario, campanha_id)
            return self.repo.count_by_campanha(campanha_id, tipo)

        if not self._usuario_e_admin(usuario):
            if tipo:
                return self.repo.count_by_owner_and_tipo(usuario.id, tipo)
            return self.repo.count_by_owner(usuario.id)

        if apenas_meus:
            if tipo:
                return self.repo.count_by_owner_and_tipo(usuario.id, tipo)
            return self.repo.count_by_owner(usuario.id)

        if tipo:
            return self.repo.count_by_tipo(tipo)
        return self.repo.count_all()

    def obter_por_id(self, personagem_id: int) -> TormentaPersonagem:
        p = self.repo.get_by_id(personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        return p

    def ativar_habilidade_origem(
        self, personagem_id: int, habilidade_id: str
    ) -> TormentaHabilidadeOrigemAtivarResponse:
        """Valida a origem salva e debita o custo oficial de PM da habilidade."""
        personagem = self.obter_por_id(personagem_id)
        ficha_json = (
            personagem.ficha_json if isinstance(personagem.ficha_json, dict) else {}
        )
        origem_slug = str(ficha_json.get("origem_slug") or "").strip().lower()
        habilidade = habilidade_ativa_origem(origem_slug, habilidade_id)
        if not habilidade:
            raise DadosInvalidos(
                "A habilidade não pertence à origem atualmente salva na ficha."
            )

        custo = max(0, int(habilidade.get("custo_pm") or 0))
        pa_max = int(personagem.pa_max or 0)
        antes = int(personagem.pa_atual if personagem.pa_atual is not None else pa_max)
        if antes < custo:
            raise DadosInvalidos(f"PM insuficientes: possui {antes}, custo {custo}.")
        depois = antes - custo
        if custo:
            personagem.pa_atual = depois
            self.repo.update(personagem)

        return TormentaHabilidadeOrigemAtivarResponse(
            habilidade_id=str(habilidade.get("id") or habilidade_id),
            nome=str(habilidade.get("nome") or habilidade_id),
            origem_slug=origem_slug,
            origem_nome=str(habilidade.get("origem_nome") or origem_slug),
            custo_pm=custo,
            pa_atual_antes=antes,
            pa_atual_depois=depois,
            pa_max=pa_max,
            frequencia=str(habilidade.get("frequencia") or ""),
            duracao=str(habilidade.get("duracao") or ""),
            resumo=str(habilidade.get("resumo") or ""),
        )

    def obter_por_id_sincronizando_pm_mb(
        self, personagem_id: int
    ) -> TormentaPersonagem:
        """Carrega o personagem e persiste PM MB se divergirem do slug/nível/atributos (fichas antigas ou migração)."""
        ent = self.obter_por_id(personagem_id)
        antes_max = int(ent.pa_max or 0)
        antes_atual = int(ent.pa_atual or 0)
        self._sincronizar_pontos_magia_mb(ent)
        depois_max = int(ent.pa_max or 0)
        depois_atual = int(ent.pa_atual or 0)
        if depois_max != antes_max or depois_atual != antes_atual:
            commit_with_rollback(self.repo.db)
            self.repo.db.refresh(ent)
        return ent

    def criar(
        self, usuario: Usuario, payload: TormentaPersonagemCreate
    ) -> TormentaPersonagemResponse:
        self._validar_tipo(payload.tipo)
        if (
            not self._usuario_pode_mestrar_tormenta(usuario)
            and payload.tipo.lower() != "jogador"
        ):
            raise DadosInvalidos("Jogadores so podem criar fichas do tipo jogador")
        nome = (payload.nome or "").strip()
        if not nome:
            raise DadosInvalidos("Nome e obrigatorio")

        ficha_prep = dict(payload.ficha_json or {})

        self._validar_atributos_criacao_jogador(
            payload.tipo,
            ficha_prep,
            payload.for_valor,
            payload.des_valor,
            payload.con_valor,
            payload.int_valor,
            payload.sab_valor,
            payload.car_valor,
        )
        self._validar_pericias_t20_jogador(
            payload.tipo,
            ficha_prep,
            int(payload.nivel or 1),
            int(payload.int_valor),
            criacao=True,
        )
        self._validar_arcanista_caminho_v13(payload.tipo, ficha_prep)
        self._validar_origem_v13(payload.tipo, ficha_prep, criacao=True)
        self._validar_classes_variantes_v13(
            payload.tipo, ficha_prep, int(payload.nivel or 1)
        )
        self._validar_melhor_amigo_v13(payload.tipo, ficha_prep)
        self._validar_duende_v13(payload.tipo, ficha_prep)
        self._validar_devocao_v13(
            payload.tipo,
            ficha_prep,
            divindade_rotulo=(payload.divindade or "").strip() or None,
        )

        campanha_id = payload.campanha_id
        if campanha_id is not None:
            self._assert_mestre_da_campanha(usuario, campanha_id)

        ficha_prep = self._preparar_ficha_json_tormenta(ficha_prep)

        pv_max = payload.pv_max
        pv_atual = payload.pv_atual if payload.pv_atual is not None else pv_max
        pa_max, pa_atual = self._resolver_pa_magia_criacao(payload)

        ficha = ficha_prep

        ent = TormentaPersonagem(
            dono_id=self._resolver_dono(usuario, payload.tipo),
            campanha_id=campanha_id,
            tipo=payload.tipo.lower(),
            nome=nome,
            jogador_nome=(payload.jogador_nome or "").strip() or None,
            raca=payload.raca or "",
            classe_nivel=payload.classe_nivel or "",
            sexo=payload.sexo or "",
            idade=payload.idade or "",
            tendencia=payload.tendencia or "",
            divindade=payload.divindade or "",
            for_valor=payload.for_valor,
            des_valor=payload.des_valor,
            con_valor=payload.con_valor,
            int_valor=payload.int_valor,
            sab_valor=payload.sab_valor,
            car_valor=payload.car_valor,
            pv_max=pv_max,
            pv_atual=min(pv_atual, pv_max) if pv_max is not None else pv_atual,
            pa_max=pa_max,
            pa_atual=min(pa_atual, pa_max) if pa_max else pa_atual,
            ca=payload.ca,
            rd=payload.rd or "",
            nivel=payload.nivel,
            iniciativa=payload.iniciativa,
            deslocamento=payload.deslocamento or "",
            tamanho=payload.tamanho or "",
            fort_total=payload.fort_total,
            ref_total=payload.ref_total,
            von_total=payload.von_total,
            ficha_json=ficha,
            foto_url=(payload.foto_url or "").strip() or None,
        )
        self._sincronizar_ca_v13(ent)

        self.repo.db.add(ent)
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        self._sincronizar_poderes_v13(ent.id, dict(ent.ficha_json or {}))
        self._sincronizar_equipamentos_v13(
            ent.id, dict(ent.ficha_json or {}), int(ent.nivel or 1)
        )
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        return self._para_resposta(ent)

    def importar_do_bestiario(
        self, usuario: Usuario, payload: TormentaBestiarioImportRequest
    ) -> TormentaPersonagemResponse:
        if not self._usuario_pode_mestrar_tormenta(usuario):
            raise DadosInvalidos("Somente mestre pode importar criaturas do bestiário")
        create_payload = criar_payload_import_bestiario(
            payload.slug,
            tipo=payload.tipo,
            campanha_id=payload.campanha_id,
            nome_override=payload.nome_override,
            foto_url=payload.foto_url,
        )
        return self.criar(usuario, create_payload)

    def _snapshot_personagem(self, ent: TormentaPersonagem) -> dict:
        return {
            "id": ent.id,
            "nome": ent.nome,
            "tipo": ent.tipo,
            "nivel": ent.nivel,
            "ca": ent.ca,
            "pv_max": ent.pv_max,
            "pa_max": ent.pa_max,
            "rd": ent.rd,
            "iniciativa": ent.iniciativa,
            "deslocamento": ent.deslocamento,
            "tamanho": ent.tamanho,
            "fort_total": ent.fort_total,
            "ref_total": ent.ref_total,
            "von_total": ent.von_total,
            "for_valor": ent.for_valor,
            "des_valor": ent.des_valor,
            "con_valor": ent.con_valor,
            "int_valor": ent.int_valor,
            "sab_valor": ent.sab_valor,
            "car_valor": ent.car_valor,
            "ficha_json": dict(ent.ficha_json or {}),
        }

    def _magias_vinculos_resumo(self, personagem_id: int) -> list:
        from app.games.tormenta.services.personagem_magias_service import (
            TormentaPersonagemMagiasService,
        )

        try:
            itens = TormentaPersonagemMagiasService(self.repo.db).listar_por_personagem(
                personagem_id
            )
        except Exception:
            return []
        out = []
        for it in itens or []:
            if hasattr(it, "model_dump"):
                d = it.model_dump()
            elif isinstance(it, dict):
                d = it
            else:
                continue
            out.append(d)
        return out

    def obter_bloco_ameaca(self, personagem_id: int) -> TormentaBlocoAmeacaResponse:
        ent = self.obter_por_id(personagem_id)
        snap = self._snapshot_personagem(ent)
        fj = dict(ent.ficha_json or {})
        magias = self._magias_vinculos_resumo(personagem_id)
        texto, fonte = montar_bloco_ameaca(
            snap, ficha_json=fj, magias_vinculos=magias, preferir_override=True
        )
        return TormentaBlocoAmeacaResponse(
            personagem_id=int(ent.id),
            texto=texto,
            fonte=fonte,
            nd=obter_nd(snap, fj),
            papel_combate=obter_papel_combate(snap, fj),
        )

    def regenerar_bloco_ameaca(
        self, personagem_id: int, *, limpar_override: bool = True
    ) -> TormentaBlocoAmeacaResponse:
        ent = self.obter_por_id(personagem_id)
        fj = dict(ent.ficha_json or {})
        if limpar_override:
            fj = limpar_texto_override(fj)
        magias = self._magias_vinculos_resumo(personagem_id)
        snap = self._snapshot_personagem(ent)
        snap["ficha_json"] = fj
        # Reconsolidar ações mínimas sem apagar campos editados do mestre
        am = fj.get("ameaca") if isinstance(fj.get("ameaca"), dict) else {}
        if not am:
            fj = consolidar_ameaca_de_personagem(
                snap, ficha_json=fj, magias_vinculos=magias
            )
        else:
            fj["ameaca"] = {**am, "texto_override": None}
        ent.ficha_json = fj
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        return self.obter_bloco_ameaca(personagem_id)

    def converter_para_ameaca(
        self,
        usuario: Usuario,
        personagem_id: int,
        payload: TormentaConverterAmeacaRequest,
    ) -> TormentaPersonagemResponse:
        if not self._usuario_pode_mestrar_tormenta(usuario):
            raise DadosInvalidos("Somente mestre pode converter personagem em ameaça")
        origem = self.obter_por_id(personagem_id)
        snap = self._snapshot_personagem(origem)
        magias = self._magias_vinculos_resumo(personagem_id)
        fj = consolidar_ameaca_de_personagem(
            snap,
            ficha_json=dict(origem.ficha_json or {}),
            magias_vinculos=magias,
            papel_combate=payload.papel_combate,
        )
        nome = (payload.nome_override or origem.nome or "").strip()
        if not nome:
            raise DadosInvalidos("Nome e obrigatorio")
        campanha_id = (
            payload.campanha_id
            if payload.campanha_id is not None
            else origem.campanha_id
        )
        create = TormentaPersonagemCreate(
            tipo=payload.tipo,
            nome=nome,
            campanha_id=campanha_id,
            jogador_nome=None,
            raca=origem.raca or "",
            classe_nivel=origem.classe_nivel or "",
            sexo=origem.sexo or "",
            idade=origem.idade or "",
            tendencia=origem.tendencia or "",
            divindade=origem.divindade or "",
            for_valor=int(origem.for_valor),
            des_valor=int(origem.des_valor),
            con_valor=int(origem.con_valor),
            int_valor=int(origem.int_valor),
            sab_valor=int(origem.sab_valor),
            car_valor=int(origem.car_valor),
            pv_max=int(origem.pv_max or 1),
            pv_atual=int(origem.pv_max or 1),
            pa_max=int(origem.pa_max or 0),
            pa_atual=int(origem.pa_max or 0),
            ca=int(origem.ca or 10),
            rd=origem.rd or "",
            nivel=int(origem.nivel or 1),
            iniciativa=int(origem.iniciativa or 0),
            deslocamento=origem.deslocamento or "",
            tamanho=origem.tamanho or "",
            fort_total=int(origem.fort_total or 0),
            ref_total=int(origem.ref_total or 0),
            von_total=int(origem.von_total or 0),
            ficha_json=fj,
            foto_url=origem.foto_url,
        )
        return self.criar(usuario, create)

    def atualizar(
        self, personagem_id: int, payload: TormentaPersonagemUpdate
    ) -> TormentaPersonagemResponse:
        ent = self.obter_por_id(personagem_id)
        data = payload.model_dump(exclude_unset=True)

        tipo_final = (data.get("tipo", ent.tipo) or "").lower()
        fv = int(data["for_valor"]) if "for_valor" in data else int(ent.for_valor)
        dv = int(data["des_valor"]) if "des_valor" in data else int(ent.des_valor)
        cv = int(data["con_valor"]) if "con_valor" in data else int(ent.con_valor)
        iv = int(data["int_valor"]) if "int_valor" in data else int(ent.int_valor)
        sv = int(data["sab_valor"]) if "sab_valor" in data else int(ent.sab_valor)
        cav = int(data["car_valor"]) if "car_valor" in data else int(ent.car_valor)
        fj = dict(ent.ficha_json or {})
        if "ficha_json" in data and data["ficha_json"] is not None:
            fj.update(dict(data["ficha_json"] or {}))
        if self._patch_mexe_compra_pontos(data):
            self._validar_atributos_criacao_jogador(
                tipo_final,
                fj,
                fv,
                dv,
                cv,
                iv,
                sv,
                cav,
            )
        nv_final = int(data["nivel"]) if "nivel" in data else int(ent.nivel or 1)
        if self._patch_mexe_pericias_mb(data):
            self._validar_pericias_t20_jogador(tipo_final, fj, nv_final, iv)
        if "ficha_json" in data:
            self._validar_arcanista_caminho_v13(tipo_final, fj)
            self._validar_origem_v13(tipo_final, fj)
            self._validar_classes_variantes_v13(tipo_final, fj, nv_final)
            self._validar_melhor_amigo_v13(tipo_final, fj)
            self._validar_duende_v13(tipo_final, fj)
            div_rot = str(data.get("divindade", ent.divindade) or "").strip() or None
            self._validar_devocao_v13(tipo_final, fj, divindade_rotulo=div_rot)
        fj = self._preparar_ficha_json_tormenta(fj)
        if "ficha_json" in data:
            data["ficha_json"] = fj

        if "foto_url" in data:
            raw = data["foto_url"]
            data["foto_url"] = None if raw is None else ((str(raw)).strip() or None)

        if "nome" in data:
            nome = (data.pop("nome") or "").strip()
            if not nome:
                raise DadosInvalidos("Nome e obrigatorio")
            ent.nome = nome

        if "ficha_json" in data:
            ent.ficha_json = dict(data.pop("ficha_json") or {})

        for key, val in data.items():
            setattr(ent, key, val)

        self._sincronizar_pontos_magia_mb(ent)
        self._sincronizar_ca_v13(ent)

        if ent.pv_max is not None and ent.pv_atual is not None:
            ent.pv_atual = min(ent.pv_atual, ent.pv_max)
        if ent.pa_max is not None and ent.pa_atual is not None:
            ent.pa_atual = min(ent.pa_atual, ent.pa_max)

        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        self._sincronizar_poderes_v13(ent.id, dict(ent.ficha_json or {}))
        self._sincronizar_equipamentos_v13(
            ent.id, dict(ent.ficha_json or {}), int(ent.nivel or 1)
        )
        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        return self._para_resposta(ent)

    def excluir(self, personagem_id: int) -> None:
        from app.games.tormenta.repositories.combate_repository import (
            TormentaCombateRepository,
        )

        ent = self.obter_por_id(personagem_id)
        combate_repo = TormentaCombateRepository(self.repo.db)
        for combate in combate_repo.list_ativos_referenciando_personagem(personagem_id):
            ids_restantes = [
                int(pid)
                for pid in (combate.personagens_ids or [])
                if int(pid) != int(personagem_id)
            ]
            if not ids_restantes:
                combate.finalizar()
            else:
                combate.personagens_ids = ids_restantes
                if combate.turno_atual >= len(ids_restantes):
                    combate.turno_atual = 0
            combate_repo.update(combate)
        self.repo.delete(ent)
