"""Regras de negócio — personagens Tormenta 20."""

from __future__ import annotations

from typing import List, Optional

from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.ports import TormentaPersonagemRepositoryProtocol
from app.games.tormenta.rules.atributos_t20 import (
    METODO_GERACAO_PADRAO,
    custo_total_compra_seis_atributos,
    normalizar_metodo_geracao_atributos,
    pontos_iniciais_compra,
    validar_valores_base_4d6,
)
from app.games.tormenta.rules.conjuracao_t20 import (
    classe_conjuracao_mb_registrada,
    pontos_magia_maximos_conjuracao,
)
from app.games.tormenta.rules.defesa_t20 import defesa_base_ca
from app.games.tormenta.rules.origens_t20 import (
    sincronizar_pericias_origem_ficha_json,
    validar_beneficios_origem,
)
from app.games.tormenta.rules.pericias_criacao_t20 import validar_pericias_ficha
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)
from app.games.tormenta.schemas.personagem import (
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

    def _resolver_dono(self, usuario: Usuario, tipo: str) -> Optional[int]:
        t = (tipo or "").lower()
        if usuario.perfil in (
            PerfilUsuario.ADMINISTRADOR,
            PerfilUsuario.MESTRE,
        ):
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
        """v1.3: CA base = 10 + DES (valor); armaduras da lista somam na UI."""
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
        if criacao and ficha_json.get("cadastro_dashboard"):
            return
        slug = str(ficha_json.get("tormenta_classe_mb_slug") or "").strip().lower()
        if not slug:
            return
        pericias = ficha_json.get("pericias")
        if not isinstance(pericias, list) or len(pericias) == 0:
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
        ok, motivo = validar_beneficios_origem(slug, ben)
        if not ok:
            raise DadosInvalidos(motivo or "Benefícios de origem inválidos.")

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

    def listar_todos(
        self,
        tipo: Optional[str],
        *,
        usuario: Usuario,
        skip: int = 0,
        limit: int = 100,
        apenas_meus: bool = False,
    ) -> List[TormentaPersonagemResponse]:
        if usuario.perfil == PerfilUsuario.JOGADOR:
            if tipo:
                rows = self.repo.get_by_owner_and_tipo(
                    usuario.id, tipo, skip=skip, limit=limit
                )
            else:
                rows = self.repo.get_by_owner(usuario.id, skip=skip, limit=limit)
            return [TormentaPersonagemResponse.model_validate(r) for r in rows]

        if apenas_meus:
            if tipo:
                rows = self.repo.get_by_owner_and_tipo(
                    usuario.id, tipo, skip=skip, limit=limit
                )
            else:
                rows = self.repo.get_by_owner(usuario.id, skip=skip, limit=limit)
            return [TormentaPersonagemResponse.model_validate(r) for r in rows]

        if tipo:
            rows = self.repo.get_by_tipo(tipo, skip=skip, limit=limit)
        else:
            rows = self.repo.get_all(skip=skip, limit=limit)
        return [TormentaPersonagemResponse.model_validate(r) for r in rows]

    def contar_todos(
        self,
        tipo: Optional[str],
        *,
        usuario: Usuario,
        apenas_meus: bool = False,
    ) -> int:
        if usuario.perfil == PerfilUsuario.JOGADOR:
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
            usuario.perfil == PerfilUsuario.JOGADOR
            and payload.tipo.lower() != "jogador"
        ):
            raise DadosInvalidos("Jogadores so podem criar fichas do tipo jogador")
        nome = (payload.nome or "").strip()
        if not nome:
            raise DadosInvalidos("Nome e obrigatorio")

        ficha_prep = self._preparar_ficha_json_tormenta(payload.ficha_json)

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

        pv_max = payload.pv_max
        pv_atual = payload.pv_atual if payload.pv_atual is not None else pv_max
        pa_max, pa_atual = self._resolver_pa_magia_criacao(payload)

        ficha = ficha_prep

        ent = TormentaPersonagem(
            dono_id=self._resolver_dono(usuario, payload.tipo),
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
        return TormentaPersonagemResponse.model_validate(ent)

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
        fj = self._preparar_ficha_json_tormenta(fj)
        if "ficha_json" in data:
            data["ficha_json"] = fj
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
        return TormentaPersonagemResponse.model_validate(ent)
        ent = self.obter_por_id(personagem_id)
        self.repo.delete(ent)
