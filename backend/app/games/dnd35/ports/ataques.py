"""Contratos estruturais para `AtaqueService` (ataques corpo-a-corpo e slots de magia)."""

from __future__ import annotations

from typing import List, Optional, Protocol, TypeAlias

from app.games.dnd35.models.ataque import Ataque, MagiaSlot
from app.games.dnd35.ports.repositories import CombatenteGetByIdProtocol

CombatenteRepositoryForAtaqueProtocol: TypeAlias = CombatenteGetByIdProtocol


class AtaqueRepositoryProtocol(Protocol):
    """Persistência de ataques e slots — superfície usada por `AtaqueService`."""

    def listar_por_combatente(self, combatente_id: int) -> List[Ataque]: ...

    def substituir_todos(self, combatente_id: int, ataques_data: list) -> List[Ataque]: ...

    def listar_magias_por_combatente(self, combatente_id: int) -> List[MagiaSlot]: ...

    def substituir_magias(self, combatente_id: int, slots_data: list) -> List[MagiaSlot]: ...

    def atualizar_usados(self, slot_id: int, usados: int) -> Optional[MagiaSlot]: ...
