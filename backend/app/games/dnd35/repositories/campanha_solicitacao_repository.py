"""Repository — solicitações de entrada em campanha D&D 3.5."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.dnd35.models.campanha import Campanha, CampanhaSolicitacao
from app.repositories.base import BaseRepository, commit_with_rollback


class CampanhaSolicitacaoRepository(BaseRepository[CampanhaSolicitacao]):
    def __init__(self, db: Session):
        super().__init__(CampanhaSolicitacao, db)

    def obter_pendente(
        self, personagem_id: int, campanha_id: int
    ) -> Optional[CampanhaSolicitacao]:
        return (
            self.db.query(CampanhaSolicitacao)
            .filter(
                CampanhaSolicitacao.personagem_id == personagem_id,
                CampanhaSolicitacao.campanha_id == campanha_id,
                CampanhaSolicitacao.status == "pendente",
            )
            .first()
        )

    def obter_pendente_por_personagem(
        self, personagem_id: int
    ) -> Optional[CampanhaSolicitacao]:
        return (
            self.db.query(CampanhaSolicitacao)
            .filter(
                CampanhaSolicitacao.personagem_id == personagem_id,
                CampanhaSolicitacao.status == "pendente",
            )
            .order_by(CampanhaSolicitacao.created_at.desc())
            .first()
        )

    def listar_pendentes_para_mestre(self, mestre_id: int) -> List[CampanhaSolicitacao]:
        return (
            self.db.query(CampanhaSolicitacao)
            .join(Campanha, CampanhaSolicitacao.campanha_id == Campanha.id)
            .filter(
                Campanha.mestre_id == mestre_id,
                CampanhaSolicitacao.status == "pendente",
            )
            .order_by(CampanhaSolicitacao.created_at.asc())
            .all()
        )

    def listar_pendentes_todas(self) -> List[CampanhaSolicitacao]:
        return (
            self.db.query(CampanhaSolicitacao)
            .filter(CampanhaSolicitacao.status == "pendente")
            .order_by(CampanhaSolicitacao.created_at.asc())
            .all()
        )

    def listar_historico_para_mestre(
        self, mestre_id: int, limit: int = 100
    ) -> List[CampanhaSolicitacao]:
        """Solicitações já resolvidas (aceita/recusada/cancelada) das mesas do mestre."""
        return (
            self.db.query(CampanhaSolicitacao)
            .join(Campanha, CampanhaSolicitacao.campanha_id == Campanha.id)
            .filter(
                Campanha.mestre_id == mestre_id,
                CampanhaSolicitacao.status != "pendente",
            )
            .order_by(CampanhaSolicitacao.resolved_at.desc().nullslast())
            .limit(limit)
            .all()
        )

    def listar_historico_todas(self, limit: int = 100) -> List[CampanhaSolicitacao]:
        return (
            self.db.query(CampanhaSolicitacao)
            .filter(CampanhaSolicitacao.status != "pendente")
            .order_by(CampanhaSolicitacao.resolved_at.desc().nullslast())
            .limit(limit)
            .all()
        )

    def obter_por_id(self, solicitacao_id: int) -> Optional[CampanhaSolicitacao]:
        return (
            self.db.query(CampanhaSolicitacao)
            .filter(CampanhaSolicitacao.id == solicitacao_id)
            .first()
        )

    def criar(self, entidade: CampanhaSolicitacao) -> CampanhaSolicitacao:
        created = self.create(entidade)
        commit_with_rollback(self.db)
        self.db.refresh(created)
        return created

    def salvar(self, entidade: CampanhaSolicitacao) -> CampanhaSolicitacao:
        updated = self.update(entidade)
        commit_with_rollback(self.db)
        self.db.refresh(updated)
        return updated
