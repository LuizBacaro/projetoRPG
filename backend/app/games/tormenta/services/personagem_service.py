"""Regras de negócio — personagens Tormenta 20."""

from __future__ import annotations

from typing import List, Optional

from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.ports import TormentaPersonagemRepositoryProtocol
from app.games.tormenta.rules.atributos_t20 import (
    custo_total_compra_seis_atributos,
    pontos_iniciais_compra,
)
from app.games.tormenta.rules.conjuracao_t20 import (
    classe_conjuracao_mb_registrada,
    pontos_magia_maximos_conjuracao,
)
from app.games.tormenta.rules.pericias_criacao_t20 import validar_pericias_ficha_mb
from app.games.tormenta.schemas.personagem import (
    TormentaPersonagemCreate,
    TormentaPersonagemResponse,
    TormentaPersonagemUpdate,
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
        """True se o PATCH altera atributos ou atributos_compra (validação de criação MB)."""
        if any(
            k in data for k in ("tipo",) + TormentaPersonagemService._CAMPOS_ATRIBUTO
        ):
            return True
        fj = data.get("ficha_json")
        return isinstance(fj, dict) and "atributos_compra" in fj

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
        nv = cls._nivel_conjuracao_mb_para_pm(fj, nivel_personagem)
        return pontos_magia_maximos_conjuracao(slug, nv, fv, dv, cv, iv, sv, carv)

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
        """Recalcula PM (Pontos de Magia) MB quando a classe MB está na tabela; zera se ainda não conjura (ex.: paladino < 5)."""
        fj = dict(ent.ficha_json or {})
        slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
        if not classe_conjuracao_mb_registrada(slug):
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
    def _validar_compra_pontos_t20_jogador(
        tipo: str,
        ficha_json: Optional[dict],
        for_valor: int,
        des_valor: int,
        con_valor: int,
        int_valor: int,
        sab_valor: int,
        car_valor: int,
    ) -> None:
        """Jogador: custo da compra 8–18 deve somar exatamente 20 pontos (MB); nao pode ultrapassar."""
        if (tipo or "").lower() != "jogador":
            return
        fv, dv, cv, iv, sv, cav = TormentaPersonagemService._seis_valores_compra_pontos(
            ficha_json, for_valor, des_valor, con_valor, int_valor, sab_valor, car_valor
        )
        meta = pontos_iniciais_compra()
        total = custo_total_compra_seis_atributos(fv, dv, cv, iv, sv, cav)
        if total is None:
            raise DadosInvalidos(
                "Ficha tipo jogador: cada valor em atributos_compra (ou atributo do personagem) "
                "usado na soma deve estar entre 8 e 18 (compra por pontos do Modulo Basico)."
            )
        if int(total) > int(meta):
            raise DadosInvalidos(
                f"Ficha tipo jogador: custo na compra por pontos nao pode ultrapassar {meta} "
                f"(gasto atual: {total}). Ajuste ficha_json.atributos_compra ou os seis atributos."
            )
        if int(total) < int(meta):
            raise DadosInvalidos(
                f"Ficha tipo jogador: e obrigatorio gastar os {meta} pontos na compra por pontos do MB "
                f"(gasto atual: {total}). Ajuste ficha_json.atributos_compra ou os seis atributos."
            )

    @staticmethod
    def _validar_pericias_t20_jogador(
        tipo: str,
        ficha_json: Optional[dict],
        nivel: int,
        int_valor: int,
    ) -> None:
        """Jogador com classe MB: valida vagas treinadas e graduações de perícias."""
        if (tipo or "").lower() != "jogador":
            return
        if not ficha_json:
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
        ok, motivo, _ = validar_pericias_ficha_mb(
            nivel=int(nivel or 1),
            slug_classe=slug,
            int_valor=int(int_valor),
            slug_raca=raca_slug,
            pericias=pericias,
        )
        if not ok:
            raise DadosInvalidos(motivo or "Orçamento de perícias MB inválido.")

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

        self._validar_compra_pontos_t20_jogador(
            payload.tipo,
            dict(payload.ficha_json or {}),
            payload.for_valor,
            payload.des_valor,
            payload.con_valor,
            payload.int_valor,
            payload.sab_valor,
            payload.car_valor,
        )
        self._validar_pericias_t20_jogador(
            payload.tipo,
            dict(payload.ficha_json or {}),
            int(payload.nivel or 1),
            int(payload.int_valor),
        )

        pv_max = payload.pv_max
        pv_atual = payload.pv_atual if payload.pv_atual is not None else pv_max
        pa_max, pa_atual = self._resolver_pa_magia_criacao(payload)

        ficha = dict(payload.ficha_json or {})

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

        self.repo.db.add(ent)
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
        if self._patch_mexe_compra_pontos(data):
            self._validar_compra_pontos_t20_jogador(
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

        if ent.pv_max is not None and ent.pv_atual is not None:
            ent.pv_atual = min(ent.pv_atual, ent.pv_max)
        if ent.pa_max is not None and ent.pa_atual is not None:
            ent.pa_atual = min(ent.pa_atual, ent.pa_max)

        commit_with_rollback(self.repo.db)
        self.repo.db.refresh(ent)
        return TormentaPersonagemResponse.model_validate(ent)

    def excluir(self, personagem_id: int) -> None:
        ent = self.obter_por_id(personagem_id)
        self.repo.delete(ent)
