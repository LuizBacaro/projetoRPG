"""Repository — personagens D&D 5e."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.dnd5e.models.personagem import Dnd5ePersonagem
from app.repositories.base import BaseRepository


class Dnd5ePersonagemRepository(BaseRepository[Dnd5ePersonagem]):
    def __init__(self, db: Session):
        super().__init__(Dnd5ePersonagem, db)

    def get_by_owner(
        self, dono_id: int, skip: int = 0, limit: int = 100
    ) -> List[Dnd5ePersonagem]:
        return (
            self.db.query(Dnd5ePersonagem)
            .filter(Dnd5ePersonagem.dono_id == dono_id)
            .order_by(Dnd5ePersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner_and_tipo(
        self, dono_id: int, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[Dnd5ePersonagem]:
        return (
            self.db.query(Dnd5ePersonagem)
            .filter(
                Dnd5ePersonagem.dono_id == dono_id,
                Dnd5ePersonagem.tipo == tipo,
            )
            .order_by(Dnd5ePersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_owner(self, dono_id: int) -> int:
        return (
            self.db.query(Dnd5ePersonagem)
            .filter(Dnd5ePersonagem.dono_id == dono_id)
            .count()
        )

    def count_by_owner_and_tipo(self, dono_id: int, tipo: str) -> int:
        return (
            self.db.query(Dnd5ePersonagem)
            .filter(
                Dnd5ePersonagem.dono_id == dono_id,
                Dnd5ePersonagem.tipo == tipo,
            )
            .count()
        )

    def count_by_tipo(self, tipo: str) -> int:
        return (
            self.db.query(Dnd5ePersonagem).filter(Dnd5ePersonagem.tipo == tipo).count()
        )

    def count_all(self) -> int:
        return self.db.query(Dnd5ePersonagem).count()

    def get_by_tipo(
        self, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[Dnd5ePersonagem]:
        return (
            self.db.query(Dnd5ePersonagem)
            .filter(Dnd5ePersonagem.tipo == tipo)
            .order_by(Dnd5ePersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Dnd5ePersonagem]:
        return (
            self.db.query(Dnd5ePersonagem)
            .order_by(Dnd5ePersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_id(self, entity_id: int) -> Optional[Dnd5ePersonagem]:
        return (
            self.db.query(Dnd5ePersonagem)
            .filter(Dnd5ePersonagem.id == entity_id)
            .first()
        )
