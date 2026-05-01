"""Repository — combates GURPS."""

from typing import Optional

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.games.gurps.models.combate import GurpsCombate
from app.repositories.base import BaseRepository, commit_with_rollback


class GurpsCombateRepository(BaseRepository[GurpsCombate]):
    def __init__(self, db: Session):
        super().__init__(GurpsCombate, db)

    def get_ativo(self) -> Optional[GurpsCombate]:
        return self.db.query(GurpsCombate).filter(GurpsCombate.ativo == True).first()

    def existe_combate_ativo(self) -> bool:
        return self.get_ativo() is not None

    def finalizar_todos(self) -> int:
        result = self.db.execute(
            update(GurpsCombate)
            .where(GurpsCombate.ativo == True)
            .values(ativo=False)
            .execution_options(synchronize_session="fetch")
        )
        commit_with_rollback(self.db)
        return result.rowcount
