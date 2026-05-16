"""Contratos estruturais para catálogo de consumíveis e vínculo ao combatente."""

from __future__ import annotations

from typing import Protocol

from app.games.dnd35.models.consumivel import Consumivel, ConsumivelJogador


class ConsumivelCatalogProtocol(Protocol):
    """Catálogo global de consumíveis — usado por `ConsumivelService`."""

    def criar(self, payload: dict) -> Consumivel:
        ...

    def obter(self, consumivel_id: int) -> Consumivel | None:
        ...

    def obter_por_nome(self, nome: str) -> Consumivel | None:
        ...

    def listar(
        self,
        skip: int,
        limit: int,
        tipo: str | None = None,
        categoria: str | None = None,
        busca: str | None = None,
    ) -> list[Consumivel]:
        ...

    def deletar(self, consumivel_id: int) -> bool:
        ...


class ConsumivelJogadorLinksProtocol(Protocol):
    """Vínculos combatente ↔ consumível — usado por `ConsumivelService`."""

    def adicionar(
        self, combatente_id: int, consumivel_id: int, quantidade: int
    ) -> ConsumivelJogador:
        ...

    def listar_detalhado(self, combatente_id: int) -> list[dict]:
        ...

    def remover(self, combatente_id: int, consumivel_id: int) -> bool:
        ...
