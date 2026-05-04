"""Repository — personagens GURPS."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.gurps.core.ordem_combate import ordenar_personagens_para_turno_gurps
from app.games.gurps.models.personagem import GurpsPersonagem
from app.repositories.base import BaseRepository


class GurpsPersonagemRepository(BaseRepository[GurpsPersonagem]):
    def __init__(self, db: Session):
        super().__init__(GurpsPersonagem, db)

    def get_by_ids(self, ids: List[int]) -> List[GurpsPersonagem]:
        if not ids:
            return []
        return (
            self.db.query(GurpsPersonagem)
            .filter(GurpsPersonagem.id.in_(ids))
            .all()
        )

    def get_by_owner(
        self, dono_id: int, skip: int = 0, limit: int = 100
    ) -> List[GurpsPersonagem]:
        return (
            self.db.query(GurpsPersonagem)
            .filter(GurpsPersonagem.dono_id == dono_id)
            .order_by(GurpsPersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_owner_and_tipo(
        self, dono_id: int, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[GurpsPersonagem]:
        return (
            self.db.query(GurpsPersonagem)
            .filter(
                GurpsPersonagem.dono_id == dono_id,
                GurpsPersonagem.tipo == tipo,
            )
            .order_by(GurpsPersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def count_by_owner(self, dono_id: int) -> int:
        return (
            self.db.query(GurpsPersonagem)
            .filter(GurpsPersonagem.dono_id == dono_id)
            .count()
        )

    def count_by_owner_and_tipo(self, dono_id: int, tipo: str) -> int:
        return (
            self.db.query(GurpsPersonagem)
            .filter(
                GurpsPersonagem.dono_id == dono_id,
                GurpsPersonagem.tipo == tipo,
            )
            .count()
        )

    def count_by_tipo(self, tipo: str) -> int:
        return (
            self.db.query(GurpsPersonagem)
            .filter(GurpsPersonagem.tipo == tipo)
            .count()
        )

    def count_all(self) -> int:
        return self.db.query(GurpsPersonagem).count()

    def get_by_tipo(
        self, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[GurpsPersonagem]:
        return (
            self.db.query(GurpsPersonagem)
            .filter(GurpsPersonagem.tipo == tipo)
            .order_by(GurpsPersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_all(self, skip: int = 0, limit: int = 100) -> List[GurpsPersonagem]:
        return (
            self.db.query(GurpsPersonagem)
            .order_by(GurpsPersonagem.nome.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def ordenar_para_turno_gurps(self, personagens: List[GurpsPersonagem]) -> List[GurpsPersonagem]:
        return ordenar_personagens_para_turno_gurps(personagens)
