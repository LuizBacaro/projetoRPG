"""Contrato estrutural (Protocol) para o repositório de personagens GURPS."""

from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy.orm import Session

from app.games.gurps.models.personagem import GurpsPersonagem


class GurpsPersonagemRepositoryProtocol(Protocol):
    """Superfície usada por `GurpsPersonagemService`."""

    db: Session

    def get_by_owner_and_tipo(
        self, dono_id: int, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[GurpsPersonagem]: ...

    def get_by_owner(
        self, dono_id: int, skip: int = 0, limit: int = 100
    ) -> List[GurpsPersonagem]: ...

    def get_by_tipo(self, tipo: str, skip: int = 0, limit: int = 100) -> List[GurpsPersonagem]: ...

    def get_all(self, skip: int = 0, limit: int = 100) -> List[GurpsPersonagem]: ...

    def count_by_owner_and_tipo(self, dono_id: int, tipo: str) -> int: ...

    def count_by_owner(self, dono_id: int) -> int: ...

    def count_by_tipo(self, tipo: str) -> int: ...

    def count_all(self) -> int: ...

    def get_by_id(self, entity_id: int) -> Optional[GurpsPersonagem]: ...

    def get_by_ids(self, ids: List[int]) -> List[GurpsPersonagem]: ...

    def ordenar_para_turno_gurps(
        self, personagens: List[GurpsPersonagem]
    ) -> List[GurpsPersonagem]: ...
