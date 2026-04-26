"""
Repository de Sessão de Campanha (D&D 3.5)

Localização: este módulo pertence ao pacote
`app.games.dnd35.repositories`. Existe um shim em
`app.repositories.sessao_campanha_repository` que re-exporta a classe
durante a reorganização multi-jogo.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.dnd35.models.campanha import Campanha
from app.games.dnd35.models.sessao_campanha import SessaoCampanha
from app.repositories.base import BaseRepository


class SessaoCampanhaRepository(BaseRepository[SessaoCampanha]):
    def __init__(self, db: Session):
        super().__init__(SessaoCampanha, db)

    def listar_por_mestre(self, mestre_id: int) -> List[SessaoCampanha]:
        return (
            self.db.query(SessaoCampanha)
            .join(Campanha, SessaoCampanha.campanha_id == Campanha.id)
            .filter(Campanha.mestre_id == mestre_id)
            .order_by(
                SessaoCampanha.created_at.desc(), SessaoCampanha.id.desc()
            )
            .all()
        )

    def obter_por_id_e_mestre(
        self, sessao_id: int, mestre_id: int
    ) -> Optional[SessaoCampanha]:
        return (
            self.db.query(SessaoCampanha)
            .join(Campanha, SessaoCampanha.campanha_id == Campanha.id)
            .filter(SessaoCampanha.id == sessao_id)
            .filter(Campanha.mestre_id == mestre_id)
            .first()
        )
