"""Repository — campanhas Tormenta 20."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.tormenta.models.campanha import TormentaCampanha
from app.repositories.base import BaseRepository, commit_with_rollback


class TormentaCampanhaRepository(BaseRepository[TormentaCampanha]):
    def __init__(self, db: Session):
        super().__init__(TormentaCampanha, db)

    def listar_por_mestre(self, mestre_id: int) -> List[TormentaCampanha]:
        return (
            self.db.query(TormentaCampanha)
            .filter(TormentaCampanha.mestre_id == mestre_id)
            .order_by(TormentaCampanha.nome.asc())
            .all()
        )

    def listar_todas(self) -> List[TormentaCampanha]:
        return (
            self.db.query(TormentaCampanha).order_by(TormentaCampanha.nome.asc()).all()
        )

    def obter_por_id(self, campanha_id: int) -> Optional[TormentaCampanha]:
        return (
            self.db.query(TormentaCampanha)
            .filter(TormentaCampanha.id == campanha_id)
            .first()
        )

    def obter_por_id_e_mestre(
        self, campanha_id: int, mestre_id: int
    ) -> Optional[TormentaCampanha]:
        return (
            self.db.query(TormentaCampanha)
            .filter(
                TormentaCampanha.id == campanha_id,
                TormentaCampanha.mestre_id == mestre_id,
            )
            .first()
        )

    def delete_hard(self, campanha: TormentaCampanha) -> None:
        self.db.delete(campanha)
        commit_with_rollback(self.db)
