"""Repository — handouts de campanha Tormenta 20."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.tormenta.models.campanha import TormentaCampanha, TormentaHandout
from app.repositories.base import BaseRepository


class TormentaHandoutRepository(BaseRepository[TormentaHandout]):
    def __init__(self, db: Session):
        super().__init__(TormentaHandout, db)

    def listar_por_mestre(
        self, mestre_id: int, campanha_id: Optional[int] = None
    ) -> List[TormentaHandout]:
        q = (
            self.db.query(TormentaHandout)
            .join(TormentaCampanha, TormentaHandout.campanha_id == TormentaCampanha.id)
            .filter(TormentaCampanha.mestre_id == mestre_id)
        )
        if campanha_id is not None:
            q = q.filter(TormentaHandout.campanha_id == int(campanha_id))
        return q.order_by(
            TormentaHandout.created_at.desc(),
            TormentaHandout.id.desc(),
        ).all()

    def listar_todas(self, campanha_id: Optional[int] = None) -> List[TormentaHandout]:
        q = self.db.query(TormentaHandout).join(
            TormentaCampanha, TormentaHandout.campanha_id == TormentaCampanha.id
        )
        if campanha_id is not None:
            q = q.filter(TormentaHandout.campanha_id == int(campanha_id))
        return q.order_by(
            TormentaHandout.created_at.desc(),
            TormentaHandout.id.desc(),
        ).all()

    def obter_por_id(self, handout_id: int) -> Optional[TormentaHandout]:
        return (
            self.db.query(TormentaHandout)
            .filter(TormentaHandout.id == handout_id)
            .first()
        )

    def obter_por_id_e_mestre(
        self, handout_id: int, mestre_id: int
    ) -> Optional[TormentaHandout]:
        return (
            self.db.query(TormentaHandout)
            .join(TormentaCampanha, TormentaHandout.campanha_id == TormentaCampanha.id)
            .filter(TormentaHandout.id == handout_id)
            .filter(TormentaCampanha.mestre_id == mestre_id)
            .first()
        )
