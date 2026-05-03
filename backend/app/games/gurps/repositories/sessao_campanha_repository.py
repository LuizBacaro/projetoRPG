"""Repository — sessões de campanha GURPS."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.gurps.models.campanha import GurpsCampanha
from app.games.gurps.models.sessao_campanha import GurpsSessaoCampanha
from app.repositories.base import BaseRepository


class GurpsSessaoCampanhaRepository(BaseRepository[GurpsSessaoCampanha]):
    def __init__(self, db: Session):
        super().__init__(GurpsSessaoCampanha, db)

    def listar_por_mestre(self, mestre_id: int) -> List[GurpsSessaoCampanha]:
        return (
            self.db.query(GurpsSessaoCampanha)
            .join(GurpsCampanha, GurpsSessaoCampanha.campanha_id == GurpsCampanha.id)
            .filter(GurpsCampanha.mestre_id == mestre_id)
            .order_by(
                GurpsSessaoCampanha.created_at.desc(),
                GurpsSessaoCampanha.id.desc(),
            )
            .all()
        )

    def listar_todas(self) -> List[GurpsSessaoCampanha]:
        return (
            self.db.query(GurpsSessaoCampanha)
            .join(GurpsCampanha, GurpsSessaoCampanha.campanha_id == GurpsCampanha.id)
            .order_by(
                GurpsSessaoCampanha.created_at.desc(),
                GurpsSessaoCampanha.id.desc(),
            )
            .all()
        )

    def obter_por_id(self, sessao_id: int) -> Optional[GurpsSessaoCampanha]:
        return (
            self.db.query(GurpsSessaoCampanha)
            .filter(GurpsSessaoCampanha.id == sessao_id)
            .first()
        )

    def obter_por_id_e_mestre(
        self, sessao_id: int, mestre_id: int
    ) -> Optional[GurpsSessaoCampanha]:
        return (
            self.db.query(GurpsSessaoCampanha)
            .join(GurpsCampanha, GurpsSessaoCampanha.campanha_id == GurpsCampanha.id)
            .filter(GurpsSessaoCampanha.id == sessao_id)
            .filter(GurpsCampanha.mestre_id == mestre_id)
            .first()
        )
