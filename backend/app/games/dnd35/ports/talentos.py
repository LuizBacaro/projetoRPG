"""Contratos estruturais (Protocol) para catálogo de talentos e vínculo ao combatente."""

from __future__ import annotations

from typing import Any, List, Optional, Protocol

from app.games.dnd35.models.talento import Talento, TalentoJogador
from app.games.dnd35.schemas.talento import TalentoCreate, TalentoJogadorCreate


class TalentoCatalogProtocol(Protocol):
    """Catálogo de talentos — usado por `TalentoService`."""

    def obter_talento_por_nome(self, nome: str) -> Optional[Talento]: ...

    def restaurar_talento(self, db_talento: Talento, talento: TalentoCreate) -> Talento: ...

    def criar_talento(self, talento: TalentoCreate) -> Talento: ...

    def listar_talentos(self, skip: int = 0, limit: int = 100) -> List[Talento]: ...

    def obter_talento(self, talento_id: int) -> Optional[Talento]: ...


class TalentoJogadorLinksProtocol(Protocol):
    """Vínculos combatente ↔ talento — usado por `TalentoService`."""

    def adicionar_talento(
        self, combatente_id: int, talento_jogador: TalentoJogadorCreate
    ) -> TalentoJogador: ...

    def obter_talentos_jogador_detalhado(self, combatente_id: int) -> List[dict[str, Any]]: ...

    def remover_talento(self, combatente_id: int, talento_id: int) -> bool: ...
