"""Repository — solicitações de entrada em campanha GURPS."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.gurps.models.campanha import GurpsCampanha, GurpsCampanhaSolicitacao
from app.repositories.base import BaseRepository, commit_with_rollback


class GurpsCampanhaSolicitacaoRepository(BaseRepository[GurpsCampanhaSolicitacao]):
    def __init__(self, db: Session):
        super().__init__(GurpsCampanhaSolicitacao, db)

    def obter_pendente(
        self, personagem_id: int, campanha_id: int
    ) -> Optional[GurpsCampanhaSolicitacao]:
        return (
            self.db.query(GurpsCampanhaSolicitacao)
            .filter(
                GurpsCampanhaSolicitacao.personagem_id == personagem_id,
                GurpsCampanhaSolicitacao.campanha_id == campanha_id,
                GurpsCampanhaSolicitacao.status == "pendente",
            )
            .first()
        )

    def obter_pendente_por_personagem(
        self, personagem_id: int
    ) -> Optional[GurpsCampanhaSolicitacao]:
        return (
            self.db.query(GurpsCampanhaSolicitacao)
            .filter(
                GurpsCampanhaSolicitacao.personagem_id == personagem_id,
                GurpsCampanhaSolicitacao.status == "pendente",
            )
            .order_by(GurpsCampanhaSolicitacao.created_at.desc())
            .first()
        )

    def listar_pendentes_para_mestre(
        self, mestre_id: int
    ) -> List[GurpsCampanhaSolicitacao]:
        return (
            self.db.query(GurpsCampanhaSolicitacao)
            .join(
                GurpsCampanha, GurpsCampanhaSolicitacao.campanha_id == GurpsCampanha.id
            )
            .filter(
                GurpsCampanha.mestre_id == mestre_id,
                GurpsCampanhaSolicitacao.status == "pendente",
            )
            .order_by(GurpsCampanhaSolicitacao.created_at.asc())
            .all()
        )

    def listar_pendentes_todas(self) -> List[GurpsCampanhaSolicitacao]:
        return (
            self.db.query(GurpsCampanhaSolicitacao)
            .filter(GurpsCampanhaSolicitacao.status == "pendente")
            .order_by(GurpsCampanhaSolicitacao.created_at.asc())
            .all()
        )

    def listar_historico_para_mestre(
        self, mestre_id: int, limit: int = 100
    ) -> List[GurpsCampanhaSolicitacao]:
        """Solicitações já resolvidas (aceita/recusada/cancelada) das mesas do mestre."""
        return (
            self.db.query(GurpsCampanhaSolicitacao)
            .join(
                GurpsCampanha, GurpsCampanhaSolicitacao.campanha_id == GurpsCampanha.id
            )
            .filter(
                GurpsCampanha.mestre_id == mestre_id,
                GurpsCampanhaSolicitacao.status != "pendente",
            )
            .order_by(GurpsCampanhaSolicitacao.resolved_at.desc().nullslast())
            .limit(limit)
            .all()
        )

    def listar_historico_todas(
        self, limit: int = 100
    ) -> List[GurpsCampanhaSolicitacao]:
        return (
            self.db.query(GurpsCampanhaSolicitacao)
            .filter(GurpsCampanhaSolicitacao.status != "pendente")
            .order_by(GurpsCampanhaSolicitacao.resolved_at.desc().nullslast())
            .limit(limit)
            .all()
        )

    def obter_por_id(self, solicitacao_id: int) -> Optional[GurpsCampanhaSolicitacao]:
        return (
            self.db.query(GurpsCampanhaSolicitacao)
            .filter(GurpsCampanhaSolicitacao.id == solicitacao_id)
            .first()
        )

    def criar(self, entidade: GurpsCampanhaSolicitacao) -> GurpsCampanhaSolicitacao:
        created = self.create(entidade)
        commit_with_rollback(self.db)
        self.db.refresh(created)
        return created

    def salvar(self, entidade: GurpsCampanhaSolicitacao) -> GurpsCampanhaSolicitacao:
        updated = self.update(entidade)
        commit_with_rollback(self.db)
        self.db.refresh(updated)
        return updated
