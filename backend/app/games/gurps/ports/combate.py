"""Contrato estrutural (Protocol) para combate GURPS."""

from __future__ import annotations

from typing import Optional, Protocol

from sqlalchemy.orm import Session

from app.games.gurps.models.combate import GurpsCombate


class GurpsCombateRepositoryProtocol(Protocol):
    """Superfície usada por `GurpsCombateService`."""

    db: Session

    def existe_combate_ativo(self) -> bool:
        ...

    def create(self, combate: GurpsCombate) -> GurpsCombate:
        ...

    def get_ativo(self) -> Optional[GurpsCombate]:
        ...

    def update(self, combate: GurpsCombate) -> GurpsCombate:
        ...
