"""Repository — campanhas GURPS."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.gurps.models.campanha import GurpsCampanha
from app.repositories.base import BaseRepository, commit_with_rollback


class GurpsCampanhaRepository(BaseRepository[GurpsCampanha]):
    def __init__(self, db: Session):
        super().__init__(GurpsCampanha, db)

    def listar_por_mestre(self, mestre_id: int) -> List[GurpsCampanha]:
        return (
            self.db.query(GurpsCampanha)
            .filter(GurpsCampanha.mestre_id == mestre_id)
            .order_by(GurpsCampanha.nome.asc())
            .all()
        )

    def listar_todas(self) -> List[GurpsCampanha]:
        return (
            self.db.query(GurpsCampanha).order_by(GurpsCampanha.nome.asc()).all()
        )

    def obter_por_id(self, campanha_id: int) -> Optional[GurpsCampanha]:
        return (
            self.db.query(GurpsCampanha)
            .filter(GurpsCampanha.id == campanha_id)
            .first()
        )

    def obter_por_id_e_mestre(
        self, campanha_id: int, mestre_id: int
    ) -> Optional[GurpsCampanha]:
        return (
            self.db.query(GurpsCampanha)
            .filter(
                GurpsCampanha.id == campanha_id,
                GurpsCampanha.mestre_id == mestre_id,
            )
            .first()
        )

    def delete_hard(self, campanha: GurpsCampanha) -> None:
        self.db.delete(campanha)
        commit_with_rollback(self.db)
