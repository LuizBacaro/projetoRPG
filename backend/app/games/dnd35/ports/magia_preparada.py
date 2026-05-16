"""Contrato estrutural (Protocol) para `MagiaPreparadaRepository`."""

from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy.orm import Session

from app.games.dnd35.models.ataque import MagiaPreparada


class MagiaPreparadaRepositoryProtocol(Protocol):
    """Superfície usada pelos endpoints de magias preparadas."""

    db: Session

    def listar_por_combatente(self, combatente_id: int) -> List[MagiaPreparada]:
        ...

    def obter_por_combatente_e_magia(
        self, combatente_id: int, magia_id: int
    ) -> Optional[MagiaPreparada]:
        ...

    def obter_por_id(self, preparada_id: int) -> Optional[MagiaPreparada]:
        ...

    def commit_refresh(self, registro: MagiaPreparada) -> MagiaPreparada:
        ...

    def add_commit_refresh(self, nova: MagiaPreparada) -> MagiaPreparada:
        ...

    def delete(self, registro: MagiaPreparada) -> None:
        ...

    def delete_all_por_combatente(self, combatente_id: int) -> int:
        ...

    def reset_slots_usados(self, combatente_id: int) -> None:
        ...

    def commit(self) -> None:
        ...
