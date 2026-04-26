"""
Repository para Campanha
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from .base import BaseRepository
from ..models.campanha import Campanha


class CampanhaRepository(BaseRepository[Campanha]):
    def __init__(self, db: Session):
        super().__init__(Campanha, db)

    def listar_por_mestre(self, mestre_id: int) -> List[Campanha]:
        return (
            self.db.query(Campanha)
            .filter(Campanha.mestre_id == mestre_id)
            .order_by(Campanha.nome.asc())
            .all()
        )

    def obter_por_id_e_mestre(self, campanha_id: int, mestre_id: int) -> Optional[Campanha]:
        return (
            self.db.query(Campanha)
            .filter(Campanha.id == campanha_id, Campanha.mestre_id == mestre_id)
            .first()
        )
