"""Repository — solicitações de entrada em campanha Tormenta 20."""

from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.tormenta.models.campanha import (
    TormentaCampanha,
    TormentaCampanhaSolicitacao,
)
from app.repositories.base import BaseRepository, commit_with_rollback


class TormentaCampanhaSolicitacaoRepository(
    BaseRepository[TormentaCampanhaSolicitacao]
):
    def __init__(self, db: Session):
        super().__init__(TormentaCampanhaSolicitacao, db)

    def obter_pendente(
        self, personagem_id: int, campanha_id: int
    ) -> Optional[TormentaCampanhaSolicitacao]:
        return (
            self.db.query(TormentaCampanhaSolicitacao)
            .filter(
                TormentaCampanhaSolicitacao.personagem_id == personagem_id,
                TormentaCampanhaSolicitacao.campanha_id == campanha_id,
                TormentaCampanhaSolicitacao.status == "pendente",
            )
            .first()
        )

    def obter_pendente_por_personagem(
        self, personagem_id: int
    ) -> Optional[TormentaCampanhaSolicitacao]:
        return (
            self.db.query(TormentaCampanhaSolicitacao)
            .filter(
                TormentaCampanhaSolicitacao.personagem_id == personagem_id,
                TormentaCampanhaSolicitacao.status == "pendente",
            )
            .order_by(TormentaCampanhaSolicitacao.created_at.desc())
            .first()
        )

    def listar_pendentes_para_mestre(
        self, mestre_id: int
    ) -> List[TormentaCampanhaSolicitacao]:
        return (
            self.db.query(TormentaCampanhaSolicitacao)
            .join(
                TormentaCampanha,
                TormentaCampanhaSolicitacao.campanha_id == TormentaCampanha.id,
            )
            .filter(
                TormentaCampanha.mestre_id == mestre_id,
                TormentaCampanhaSolicitacao.status == "pendente",
            )
            .order_by(TormentaCampanhaSolicitacao.created_at.asc())
            .all()
        )

    def listar_pendentes_todas(self) -> List[TormentaCampanhaSolicitacao]:
        return (
            self.db.query(TormentaCampanhaSolicitacao)
            .filter(TormentaCampanhaSolicitacao.status == "pendente")
            .order_by(TormentaCampanhaSolicitacao.created_at.asc())
            .all()
        )

    def listar_historico_para_mestre(
        self, mestre_id: int, limit: int = 100
    ) -> List[TormentaCampanhaSolicitacao]:
        """Solicitações já resolvidas (aceita/recusada/cancelada) das mesas do mestre."""
        return (
            self.db.query(TormentaCampanhaSolicitacao)
            .join(
                TormentaCampanha,
                TormentaCampanhaSolicitacao.campanha_id == TormentaCampanha.id,
            )
            .filter(
                TormentaCampanha.mestre_id == mestre_id,
                TormentaCampanhaSolicitacao.status != "pendente",
            )
            .order_by(TormentaCampanhaSolicitacao.resolved_at.desc().nullslast())
            .limit(limit)
            .all()
        )

    def listar_historico_todas(
        self, limit: int = 100
    ) -> List[TormentaCampanhaSolicitacao]:
        return (
            self.db.query(TormentaCampanhaSolicitacao)
            .filter(TormentaCampanhaSolicitacao.status != "pendente")
            .order_by(TormentaCampanhaSolicitacao.resolved_at.desc().nullslast())
            .limit(limit)
            .all()
        )

    def obter_por_id(
        self, solicitacao_id: int
    ) -> Optional[TormentaCampanhaSolicitacao]:
        return (
            self.db.query(TormentaCampanhaSolicitacao)
            .filter(TormentaCampanhaSolicitacao.id == solicitacao_id)
            .first()
        )

    def criar(
        self, entidade: TormentaCampanhaSolicitacao
    ) -> TormentaCampanhaSolicitacao:
        created = self.create(entidade)
        commit_with_rollback(self.db)
        self.db.refresh(created)
        return created

    def salvar(
        self, entidade: TormentaCampanhaSolicitacao
    ) -> TormentaCampanhaSolicitacao:
        updated = self.update(entidade)
        commit_with_rollback(self.db)
        self.db.refresh(updated)
        return updated
