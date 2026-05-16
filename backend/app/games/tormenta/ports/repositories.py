"""Contrato do repositório de personagens Tormenta."""

from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy.orm import Session

from app.games.tormenta.models.personagem import TormentaPersonagem


class TormentaPersonagemRepositoryProtocol(Protocol):
    db: Session

    def get_by_owner_and_tipo(
        self, dono_id: int, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[TormentaPersonagem]: ...

    def get_by_owner(
        self, dono_id: int, skip: int = 0, limit: int = 100
    ) -> List[TormentaPersonagem]: ...

    def get_by_tipo(
        self, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[TormentaPersonagem]: ...

    def get_all(self, skip: int = 0, limit: int = 100) -> List[TormentaPersonagem]: ...

    def count_by_owner_and_tipo(self, dono_id: int, tipo: str) -> int: ...

    def count_by_owner(self, dono_id: int) -> int: ...

    def count_by_tipo(self, tipo: str) -> int: ...

    def count_all(self) -> int: ...

    def get_by_id(self, entity_id: int) -> Optional[TormentaPersonagem]: ...

    def delete(self, entity: TormentaPersonagem) -> bool: ...
