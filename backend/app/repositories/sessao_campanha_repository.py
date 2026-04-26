"""
Repository para Sessao de Campanha.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from .base import BaseRepository
from ..models.campanha import Campanha
from ..models.sessao_campanha import SessaoCampanha


class SessaoCampanhaRepository(BaseRepository[SessaoCampanha]):
    def __init__(self, db: Session):
        super().__init__(SessaoCampanha, db)

    def listar_por_mestre(self, mestre_id: int) -> List[SessaoCampanha]:
        return (
            self.db.query(SessaoCampanha)
            .join(Campanha, SessaoCampanha.campanha_id == Campanha.id)
            .filter(Campanha.mestre_id == mestre_id)
            .order_by(SessaoCampanha.created_at.desc(), SessaoCampanha.id.desc())
            .all()
        )

    def obter_por_id_e_mestre(self, sessao_id: int, mestre_id: int) -> Optional[SessaoCampanha]:
        return (
            self.db.query(SessaoCampanha)
            .join(Campanha, SessaoCampanha.campanha_id == Campanha.id)
            .filter(SessaoCampanha.id == sessao_id)
            .filter(Campanha.mestre_id == mestre_id)
            .first()
        )
