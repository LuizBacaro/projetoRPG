"""Repository — personagens Tormenta."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.tormenta.models.personagem import TormentaPersonagem
from app.repositories.base import BaseRepository


class TormentaPersonagemRepository(BaseRepository[TormentaPersonagem]):
    def __init__(self, db: Session):
        super().__init__(TormentaPersonagem, db)

    def get_by_owner(
        self, dono_id: int, skip: int = 0, limit: int = 100
    ) -> List[TormentaPersonagem]:
        return (
            self.db.query(TormentaPersonagem)
            .filter(TormentaPersonagem.dono_id == dono_id)
            .order_by(TormentaPersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner_and_tipo(
        self, dono_id: int, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[TormentaPersonagem]:
        return (
            self.db.query(TormentaPersonagem)
            .filter(
                TormentaPersonagem.dono_id == dono_id,
                TormentaPersonagem.tipo == tipo,
            )
            .order_by(TormentaPersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_owner(self, dono_id: int) -> int:
        return (
            self.db.query(TormentaPersonagem)
            .filter(TormentaPersonagem.dono_id == dono_id)
            .count()
        )

    def count_by_owner_and_tipo(self, dono_id: int, tipo: str) -> int:
        return (
            self.db.query(TormentaPersonagem)
            .filter(
                TormentaPersonagem.dono_id == dono_id,
                TormentaPersonagem.tipo == tipo,
            )
            .count()
        )

    def count_by_tipo(self, tipo: str) -> int:
        return (
            self.db.query(TormentaPersonagem)
            .filter(TormentaPersonagem.tipo == tipo)
            .count()
        )

    def count_all(self) -> int:
        return self.db.query(TormentaPersonagem).count()

    def get_by_tipo(
        self, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[TormentaPersonagem]:
        return (
            self.db.query(TormentaPersonagem)
            .filter(TormentaPersonagem.tipo == tipo)
            .order_by(TormentaPersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[TormentaPersonagem]:
        return (
            self.db.query(TormentaPersonagem)
            .order_by(TormentaPersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_campanha(
        self,
        campanha_id: int,
        tipo: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TormentaPersonagem]:
        q = self.db.query(TormentaPersonagem).filter(
            TormentaPersonagem.campanha_id == campanha_id
        )
        if tipo:
            q = q.filter(TormentaPersonagem.tipo == tipo)
        return q.order_by(TormentaPersonagem.nome.asc()).offset(skip).limit(limit).all()

    def count_by_campanha(self, campanha_id: int, tipo: Optional[str] = None) -> int:
        q = self.db.query(TormentaPersonagem).filter(
            TormentaPersonagem.campanha_id == campanha_id
        )
        if tipo:
            q = q.filter(TormentaPersonagem.tipo == tipo)
        return q.count()

    def get_by_ids(self, ids: List[int]) -> List[TormentaPersonagem]:
        if not ids:
            return []
        return (
            self.db.query(TormentaPersonagem)
            .filter(TormentaPersonagem.id.in_(ids))
            .all()
        )
