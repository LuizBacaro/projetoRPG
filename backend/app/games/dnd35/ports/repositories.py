"""Contratos estruturais (Protocol) para repositórios D&D 3.5 usados em serviços."""

from __future__ import annotations

from typing import List, Optional, Protocol

from sqlalchemy.orm import Session

from app.games.dnd35.models.combate import Combate, CombateHistorico
from app.games.dnd35.models.combatente import Combatente


class CombateRepositoryProtocol(Protocol):
    """Superfície usada por `CombateService`."""

    db: Session

    def existe_combate_ativo(self) -> bool: ...

    def create(self, combate: Combate) -> Combate: ...

    def get_ativo(self) -> Optional[Combate]: ...

    def update(self, combate: Combate) -> Combate: ...

    def criar_historico(self, historico: CombateHistorico) -> CombateHistorico: ...

    def listar_historico(
        self, skip: int = 0, limit: int = 20
    ) -> List[CombateHistorico]: ...

    def contar_historico(self) -> int: ...


class CombatenteRepositoryForCombateProtocol(Protocol):
    """Superfície de combatentes usada apenas pelo fluxo de `CombateService`."""

    def get_by_ids(self, combatente_ids: List[int]) -> List[Combatente]: ...

    def ordenar_por_iniciativa(
        self, combatentes: List[Combatente]
    ) -> List[Combatente]: ...

    def get_vivos_by_ids(self, combatente_ids: List[int]) -> List[Combatente]: ...

    def resetar_todos_hp(self) -> int: ...


class CombatenteGetByIdProtocol(Protocol):
    """Só `get_by_id` (via repositório com `apply_not_deleted`) — verificação mínima de combatente."""

    def get_by_id(self, entity_id: int) -> Optional[Combatente]: ...


class CombatenteRepositoryProtocol(CombatenteRepositoryForCombateProtocol, Protocol):
    """Superfície usada por `CombatenteService` (inclui CRUD, contagens e `db`)."""

    db: Session

    def get_by_owner_and_tipo(
        self, dono_id: int, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[Combatente]: ...

    def get_by_owner(
        self, dono_id: int, skip: int = 0, limit: int = 100
    ) -> List[Combatente]: ...

    def get_by_owner_or_campanha_mestre_and_tipo(
        self, mestre_id: int, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[Combatente]: ...

    def get_by_owner_or_campanha_mestre(
        self, mestre_id: int, skip: int = 0, limit: int = 100
    ) -> List[Combatente]: ...

    def get_by_tipo(
        self, tipo: str, skip: int = 0, limit: int = 100
    ) -> List[Combatente]: ...

    def get_all(self, skip: int = 0, limit: int = 100) -> List[Combatente]: ...

    def count_by_owner_and_tipo(self, dono_id: int, tipo: str) -> int: ...

    def count_by_owner(self, dono_id: int) -> int: ...

    def count_by_owner_or_campanha_mestre_and_tipo(
        self, mestre_id: int, tipo: str
    ) -> int: ...

    def count_by_owner_or_campanha_mestre(self, mestre_id: int) -> int: ...

    def count_by_tipo(self, tipo: str) -> int: ...

    def count_all(self) -> int: ...

    def get_by_id(self, entity_id: int) -> Optional[Combatente]: ...

    def create(self, combatente: Combatente) -> Combatente: ...

    def update(self, combatente: Combatente) -> Combatente: ...

    def delete(self, combatente: Combatente) -> bool: ...
