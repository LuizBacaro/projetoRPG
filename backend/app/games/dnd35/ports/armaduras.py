"""Contratos estruturais (Protocol) para catálogo de armadura/proteção e vínculo ao combatente."""

from __future__ import annotations

from typing import Any, List, Optional, Protocol

from app.games.dnd35.models.armadura_protecao import (
    ArmaduraProtecao,
    ArmaduraProtecaoJogador,
)
from app.games.dnd35.schemas.armadura_protecao import (
    ArmaduraProtecaoCreate,
    ArmaduraProtecaoJogadorCreate,
)


class ArmaduraProtecaoCatalogProtocol(Protocol):
    """Catálogo global de itens de proteção — usado por `ArmaduraProtecaoService`."""

    def criar_item(self, item: ArmaduraProtecaoCreate) -> ArmaduraProtecao:
        ...

    def obter_por_id(self, item_id: int) -> Optional[ArmaduraProtecao]:
        ...

    def listar(self, skip: int = 0, limit: int = 100) -> List[ArmaduraProtecao]:
        ...


class ArmaduraProtecaoJogadorLinksProtocol(Protocol):
    """Vínculos combatente ↔ item — usado por `ArmaduraProtecaoService`."""

    def adicionar_item(
        self, combatente_id: int, payload: ArmaduraProtecaoJogadorCreate
    ) -> ArmaduraProtecaoJogador:
        ...

    def listar_detalhado(self, combatente_id: int) -> List[dict[str, Any]]:
        ...

    def remover_item(self, combatente_id: int, item_id: int) -> bool:
        ...
