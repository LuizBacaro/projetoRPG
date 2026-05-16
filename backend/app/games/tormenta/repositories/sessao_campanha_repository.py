"""Repository — sessões de campanha Tormenta 20."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.tormenta.models.campanha import TormentaCampanha, TormentaSessaoCampanha
from app.repositories.base import BaseRepository


class TormentaSessaoCampanhaRepository(BaseRepository[TormentaSessaoCampanha]):
    def __init__(self, db: Session):
        super().__init__(TormentaSessaoCampanha, db)

    def listar_por_mestre(self, mestre_id: int) -> List[TormentaSessaoCampanha]:
        return (
            self.db.query(TormentaSessaoCampanha)
            .join(
                TormentaCampanha,
                TormentaSessaoCampanha.campanha_id == TormentaCampanha.id,
            )
            .filter(TormentaCampanha.mestre_id == mestre_id)
            .order_by(
                TormentaSessaoCampanha.created_at.desc(),
                TormentaSessaoCampanha.id.desc(),
            )
            .all()
        )

    def listar_todas(self) -> List[TormentaSessaoCampanha]:
        return (
            self.db.query(TormentaSessaoCampanha)
            .join(
                TormentaCampanha,
                TormentaSessaoCampanha.campanha_id == TormentaCampanha.id,
            )
            .order_by(
                TormentaSessaoCampanha.created_at.desc(),
                TormentaSessaoCampanha.id.desc(),
            )
            .all()
        )

    def obter_por_id(self, sessao_id: int) -> Optional[TormentaSessaoCampanha]:
        return (
            self.db.query(TormentaSessaoCampanha)
            .filter(TormentaSessaoCampanha.id == sessao_id)
            .first()
        )

    def obter_por_id_e_mestre(
        self, sessao_id: int, mestre_id: int
    ) -> Optional[TormentaSessaoCampanha]:
        return (
            self.db.query(TormentaSessaoCampanha)
            .join(
                TormentaCampanha,
                TormentaSessaoCampanha.campanha_id == TormentaCampanha.id,
            )
            .filter(TormentaSessaoCampanha.id == sessao_id)
            .filter(TormentaCampanha.mestre_id == mestre_id)
            .first()
        )
