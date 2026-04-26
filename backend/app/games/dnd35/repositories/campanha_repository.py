"""
Repository de Campanha (D&D 3.5)

Localização: este módulo pertence ao pacote
`app.games.dnd35.repositories`. Existe um shim em
`app.repositories.campanha_repository` que re-exporta a classe durante
a reorganização multi-jogo.
"""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.games.dnd35.models.campanha import Campanha
from app.repositories.base import BaseRepository


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

    def obter_por_id_e_mestre(
        self, campanha_id: int, mestre_id: int
    ) -> Optional[Campanha]:
        return (
            self.db.query(Campanha)
            .filter(Campanha.id == campanha_id, Campanha.mestre_id == mestre_id)
            .first()
        )
