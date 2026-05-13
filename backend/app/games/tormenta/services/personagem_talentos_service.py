"""Regras de negócio — talentos vinculados ao personagem Tormenta 20."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.models.talento import TormentaTalento, TormentaTalentoPersonagem
from app.games.tormenta.schemas.talento_personagem import (
    TormentaMigrarTalentosJsonResponse,
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
        return TormentaTalentoPersonagemItem(
            id=row.id,
            talento_id=row.talento_id,
            nome=t.nome,
            descricao=t.descricao,
            pagina_referencia=t.pagina_referencia,
            origem_catalogo_mb=bool(t.origem_catalogo_mb),
            notas=row.notas,
            adicionado_em=row.adicionado_em,
        )

    def listar_por_personagem(self, personagem_id: int) -> List[TormentaTalentoPersonagemItem]:
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

    def adicionar_vinculo(
        self, personagem_id: int, payload: TormentaTalentoVinculoCreate
    ) -> TormentaTalentoPersonagemItem:
        if payload.talento_id is not None:
            t = self.db.get(TormentaTalento, payload.talento_id)
            if not t:
                raise DadosInvalidos("Talento nao encontrado no catalogo")
        else:
            t = self._buscar_ou_criar_talento_por_nome(payload.nome or "")

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
                "Este talento ja esta vinculado ao personagem",
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

    def migrar_talentos_mb_lista_do_json(self, personagem_id: int) -> TormentaMigrarTalentosJsonResponse:
        p = self.db.get(TormentaPersonagem, personagem_id)
        if not p:
            raise ArenaBaseException("Personagem nao encontrado", status_code=404)
        fj = p.ficha_json or {}
        raw = fj.get("talentos_mb_lista")
        if not isinstance(raw, list):
            return TormentaMigrarTalentosJsonResponse(vinculos_criados=0, ignorados_duplicados=0)

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
