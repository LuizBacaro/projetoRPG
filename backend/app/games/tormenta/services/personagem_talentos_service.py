"""Regras de negócio — talentos vinculados ao personagem Tormenta 20."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.models.talento import TormentaTalento, TormentaTalentoPersonagem
from app.games.tormenta.rules.poderes_catalogo_v13_t20 import metadados_poder_por_nome
from app.games.tormenta.rules.poderes_ficha_v13_t20 import (
    AUTO_PODER_NOTA_PREFIX,
    listar_poderes_sync_v13,
)
from app.games.tormenta.rules.poderes_herois_arton_t20 import validar_vinculo_poder_ha
from app.games.tormenta.rules.poderes_pre_requisitos_v13_t20 import (
    PersonagemPoderContext,
    contexto_poder_de_personagem,
    deve_validar_pre_requisitos_v13,
    validar_pre_requisitos_poder,
)
from app.games.tormenta.rules.regra_versao_t20 import regra_versao_de_ficha
from app.games.tormenta.schemas.talento_personagem import (
    TormentaMigrarTalentosJsonResponse,
    TormentaPoderAtivarResponse,
    TormentaTalentoPersonagemItem,
    TormentaTalentoVinculoCreate,
)
from app.repositories.base import commit_with_rollback
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos


class TormentaPersonagemTalentosService:
    """Catálogo `tormenta_talentos` + vínculos `tormenta_talentos_personagem`."""

    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _to_item(row: TormentaTalentoPersonagem) -> TormentaTalentoPersonagemItem:
        t = row.talento
        meta = metadados_poder_por_nome(t.nome, notas=row.notas)
        return TormentaTalentoPersonagemItem(
            id=row.id,
            talento_id=row.talento_id,
            nome=t.nome,
            descricao=t.descricao,
            pagina_referencia=t.pagina_referencia,
            origem_catalogo_mb=bool(t.origem_catalogo_mb),
            notas=row.notas,
            categoria_v13=meta.get("categoria_v13"),
            custo_pm=int(meta.get("custo_pm") or 0),
            adicionado_em=row.adicionado_em,
        )

    def listar_por_personagem(
        self, personagem_id: int
    ) -> List[TormentaTalentoPersonagemItem]:
        rows = (
            self.db.query(TormentaTalentoPersonagem)
            .filter(TormentaTalentoPersonagem.personagem_id == personagem_id)
            .order_by(TormentaTalentoPersonagem.adicionado_em.asc())
            .all()
        )
        return [self._to_item(r) for r in rows]

    def _buscar_talento_por_nome(self, nome: str) -> Optional[TormentaTalento]:
        n = nome.strip()
        if not n:
            return None
        row = (
            self.db.query(TormentaTalento)
            .filter(func.lower(TormentaTalento.nome) == func.lower(n))
            .first()
        )
        return row

    def _buscar_ou_criar_talento_por_nome(self, nome: str) -> TormentaTalento:
        n = nome.strip()[:200]
        if len(n) < 2:
            raise DadosInvalidos("Nome do talento deve ter pelo menos 2 caracteres")
        exist = self._buscar_talento_por_nome(n)
        if exist:
            return exist
        t = TormentaTalento(
            nome=n,
            descricao=None,
            pagina_referencia=None,
            origem_catalogo_mb=False,
        )
        self.db.add(t)
        self.db.flush()
        return t

    def _nomes_poderes_vinculados(self, personagem_id: int) -> List[str]:
        rows = (
            self.db.query(TormentaTalentoPersonagem)
            .filter(TormentaTalentoPersonagem.personagem_id == personagem_id)
            .all()
        )
        return [str(r.talento.nome) for r in rows if r.talento and r.talento.nome]

    def _validar_pre_requisitos_ao_vincular(
        self,
        personagem: TormentaPersonagem,
        nome_poder: str,
        notas: Optional[str],
    ) -> None:
        fj = personagem.ficha_json if isinstance(personagem.ficha_json, dict) else {}
        rv = regra_versao_de_ficha(fj)
        if not deve_validar_pre_requisitos_v13(regra_versao=rv, notas=notas):
            return
        ctx = contexto_poder_de_personagem(
            personagem,
            poderes_nomes_extra=self._nomes_poderes_vinculados(int(personagem.id)),
        )
        res = validar_pre_requisitos_poder(nome_poder, ctx)
        if not res.get("valido"):
            faltando = res.get("faltando") or []
            partes = [
                str(x.get("descricao") or "") for x in faltando if x.get("descricao")
            ]
            detalhe = "; ".join(partes) if partes else "pré-requisitos não atendidos"
            raise DadosInvalidos(
                f"Pré-requisitos não atendidos para «{nome_poder.strip()}»: {detalhe}."
            )

    def _validar_elegibilidade_ha_ao_vincular(
        self,
        personagem: TormentaPersonagem,
        nome_poder: str,
    ) -> None:
        fj = personagem.ficha_json if isinstance(personagem.ficha_json, dict) else {}
        validar_vinculo_poder_ha(nome_poder, fj)

    @staticmethod
    def preview_validar_pre_requisitos(body: Dict[str, Any]) -> Dict[str, Any]:
        fj = body.get("ficha_json") if isinstance(body.get("ficha_json"), dict) else {}
        rv = str(body.get("regra_versao") or regra_versao_de_ficha(fj) or "v13")
        ctx = PersonagemPoderContext(
            nivel=int(body.get("nivel") or 1),
            for_valor=int(body.get("for_valor") or 0),
            des_valor=int(body.get("des_valor") or 0),
            con_valor=int(body.get("con_valor") or 0),
            int_valor=int(body.get("int_valor") or 0),
            sab_valor=int(body.get("sab_valor") or 0),
            car_valor=int(body.get("car_valor") or 0),
            ficha_json=fj,
            poderes_nomes=list(body.get("poderes_escolhidos") or []),
            regra_versao=rv,
        )
        nome = str(body.get("nome_poder") or "").strip()
        try:
            validar_vinculo_poder_ha(nome, fj)
        except DadosInvalidos as exc:
            msg = str(getattr(exc, "message", None) or exc)
            return {
                "valido": False,
                "nome_poder": nome,
                "faltando": [],
                "pre_requisitos": [],
                "motivo": msg,
            }
        res = validar_pre_requisitos_poder(nome, ctx)
        faltando = res.get("faltando") or []
        motivo = ""
        if faltando:
            motivo = "; ".join(
                str(x.get("descricao") or "") for x in faltando if x.get("descricao")
            )
        return {
            "valido": bool(res.get("valido")),
            "nome_poder": nome,
            "faltando": faltando,
            "pre_requisitos": res.get("pre_requisitos") or [],
            "motivo": motivo,
        }

    def adicionar_vinculo(
        self, personagem_id: int, payload: TormentaTalentoVinculoCreate
    ) -> TormentaTalentoPersonagemItem:
        if payload.talento_id is not None:
            t = self.db.get(TormentaTalento, payload.talento_id)
            if not t:
                raise DadosInvalidos("Talento nao encontrado no catalogo")
        else:
            t = self._buscar_ou_criar_talento_por_nome(payload.nome or "")

        p = self.db.get(TormentaPersonagem, personagem_id)
        if p:
            self._validar_elegibilidade_ha_ao_vincular(p, t.nome)
            self._validar_pre_requisitos_ao_vincular(
                p,
                t.nome,
                (payload.notas or "").strip() or None,
            )

        dup = (
            self.db.query(TormentaTalentoPersonagem)
            .filter(
                TormentaTalentoPersonagem.personagem_id == personagem_id,
                TormentaTalentoPersonagem.talento_id == t.id,
            )
            .first()
        )
        if dup:
            raise ArenaBaseException(
                "Este talento já está vinculado ao personagem",
                status_code=409,
            )

        v = TormentaTalentoPersonagem(
            personagem_id=personagem_id,
            talento_id=t.id,
            notas=(payload.notas or "").strip() or None,
        )
        self.db.add(v)
        commit_with_rollback(self.db)
        self.db.refresh(v)
        return self._to_item(v)

    def remover_vinculo(self, personagem_id: int, vinculo_id: int) -> None:
        row = self.db.get(TormentaTalentoPersonagem, vinculo_id)
        if not row or row.personagem_id != personagem_id:
            raise ArenaBaseException("Vinculo nao encontrado", status_code=404)
        self.db.delete(row)
        commit_with_rollback(self.db)

    def migrar_talentos_mb_lista_do_json(
        self, personagem_id: int
    ) -> TormentaMigrarTalentosJsonResponse:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        fj = p.ficha_json or {}
        raw = fj.get("talentos_mb_lista")
        if not isinstance(raw, list):
            return TormentaMigrarTalentosJsonResponse(
                vinculos_criados=0, ignorados_duplicados=0
            )

        criados = 0
        dup = 0
        vistos_talento_ids: set[int] = set()
        for item in raw:
            if isinstance(item, str):
                nome = item.strip()
            elif isinstance(item, dict):
                nome = str(item.get("nome", "")).strip()
            else:
                continue
            if len(nome) < 2:
                continue
            validar_vinculo_poder_ha(nome, fj)
            t = self._buscar_ou_criar_talento_por_nome(nome)
            if t.id in vistos_talento_ids:
                dup += 1
                continue
            exist = (
                self.db.query(TormentaTalentoPersonagem)
                .filter(
                    TormentaTalentoPersonagem.personagem_id == personagem_id,
                    TormentaTalentoPersonagem.talento_id == t.id,
                )
                .first()
            )
            if exist:
                dup += 1
                continue
            self.db.add(
                TormentaTalentoPersonagem(
                    personagem_id=personagem_id,
                    talento_id=t.id,
                    notas=None,
                )
            )
            vistos_talento_ids.add(t.id)
            criados += 1
            self.db.flush()
        if criados:
            commit_with_rollback(self.db)
        return TormentaMigrarTalentosJsonResponse(
            vinculos_criados=criados,
            ignorados_duplicados=dup,
        )

    def sincronizar_poderes_automaticos_v13(
        self, personagem_id: int, ficha_json: dict
    ) -> dict:
        """Garante vínculos SQL para poderes de origem, concedido e Versátil v1.3."""
        desejados = listar_poderes_sync_v13(ficha_json)
        desejados_notas = {p["notas"] for p in desejados}

        rows = (
            self.db.query(TormentaTalentoPersonagem)
            .filter(TormentaTalentoPersonagem.personagem_id == personagem_id)
            .all()
        )

        removidos = 0
        for row in rows:
            nota = (row.notas or "").strip()
            if nota.startswith(AUTO_PODER_NOTA_PREFIX) and nota not in desejados_notas:
                self.db.delete(row)
                removidos += 1

        if removidos:
            self.db.flush()

        vinculados_talento_ids = {
            r.talento_id
            for r in self.db.query(TormentaTalentoPersonagem)
            .filter(TormentaTalentoPersonagem.personagem_id == personagem_id)
            .all()
        }
        notas_existentes = {
            (r.notas or "").strip()
            for r in self.db.query(TormentaTalentoPersonagem)
            .filter(TormentaTalentoPersonagem.personagem_id == personagem_id)
            .all()
            if (r.notas or "").strip()
        }

        criados = 0
        for pod in desejados:
            nota = pod["notas"]
            if nota in notas_existentes:
                continue
            nome = str(pod.get("nome") or "").strip()
            if len(nome) < 2:
                continue
            t = self._buscar_ou_criar_talento_por_nome(nome)
            if t.id in vinculados_talento_ids:
                continue
            self.db.add(
                TormentaTalentoPersonagem(
                    personagem_id=personagem_id,
                    talento_id=t.id,
                    notas=nota,
                )
            )
            vinculados_talento_ids.add(t.id)
            criados += 1

        if criados or removidos:
            commit_with_rollback(self.db)

        return {"vinculos_criados": criados, "vinculos_removidos": removidos}

    def ativar_poder_com_pm(
        self,
        personagem_id: int,
        vinculo_id: int,
        *,
        custo_pm_override: int | None = None,
    ) -> TormentaPoderAtivarResponse:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        row = self.db.get(TormentaTalentoPersonagem, vinculo_id)
        if not row or row.personagem_id != personagem_id:
            raise ArenaBaseException("Vinculo nao encontrado", status_code=404)
        meta = metadados_poder_por_nome(row.talento.nome, notas=row.notas)
        custo = (
            int(custo_pm_override)
            if custo_pm_override is not None
            else int(meta.get("custo_pm") or 0)
        )
        custo = max(0, min(99, custo))
        if custo <= 0:
            raise DadosInvalidos(
                "Este poder nao possui custo PM registrado no catálogo para ativação."
            )
        pa_max = int(p.pa_max or 0)
        antes = int(p.pa_atual if p.pa_atual is not None else pa_max)
        if antes < custo:
            raise DadosInvalidos(f"PM insuficientes: possui {antes}, custo {custo}.")
        depois = antes - custo
        p.pa_atual = depois
        commit_with_rollback(self.db)
        self.db.refresh(p)
        return TormentaPoderAtivarResponse(
            nome=row.talento.nome,
            custo_pm=custo,
            pa_atual_antes=antes,
            pa_atual_depois=depois,
            pa_max=pa_max,
        )
