"""Contrato estrutural (Protocol) para `CondicaoRepository`."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

from sqlalchemy.orm import Session

from app.games.dnd35.models.condicao import Condicao


class CondicaoRepositoryProtocol(Protocol):
    """Superfície usada por `CondicaoService` e opcionalmente por `CombatenteService`."""

    db: Session

    def commit(self) -> None: ...

    def get_all(self) -> List[Dict[str, Any]]: ...

    def get_by_id(self, condicao_id: int) -> Optional[Condicao]: ...

    def get_by_nome(self, nome: str) -> Optional[Condicao]: ...

    def seed(self, condicoes_data: List[Dict[str, Any]]) -> None: ...

    def get_condicoes_do_combatente(self, combatente_id: int) -> List[Dict[str, Any]]: ...

    def aplicar(
        self,
        combatente_id: int,
        condicao_id: int,
        duracao_turnos: int = -1,
        commit: bool = True,
    ) -> None: ...

    def remover(self, combatente_id: int, condicao_id: int, commit: bool = True) -> None: ...

    def remover_todas(self, combatente_id: int, commit: bool = True) -> None: ...

    def atualizar_duracao(
        self,
        combatente_id: int,
        condicao_id: int,
        nova_duracao: int,
        commit: bool = True,
    ) -> bool: ...
