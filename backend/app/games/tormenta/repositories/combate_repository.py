"""Repository — combates Tormenta (Arena)."""

from typing import Optional

from sqlalchemy.orm import Session

from app.games.tormenta.models.combate import TormentaCombate
from app.repositories.base import BaseRepository


class TormentaCombateRepository(BaseRepository[TormentaCombate]):
    def __init__(self, db: Session):
        super().__init__(TormentaCombate, db)

    def get_ativo_por_usuario(self, usuario_id: int) -> Optional[TormentaCombate]:
        return (
            self.db.query(TormentaCombate)
            .filter(
                TormentaCombate.usuario_id == usuario_id,
                TormentaCombate.ativo == True,  # noqa: E712
            )
            .order_by(TormentaCombate.id.desc())
            .first()
        )

    def existe_combate_ativo_por_usuario(self, usuario_id: int) -> bool:
        return self.get_ativo_por_usuario(usuario_id) is not None
