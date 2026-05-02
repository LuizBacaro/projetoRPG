"""Contrato estrutural (Protocol) para `GrimorioRepository` / `GrimorioService`."""

from __future__ import annotations

from typing import List, Optional, Protocol, Tuple

from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.grimorio import GrimorioHistoricoTroca, GrimorioMagia, GrimorioNotificacao


class GrimorioRepositoryProtocol(Protocol):
    """Superfície usada por `GrimorioService`."""

    def get_combatente(self, combatente_id: int) -> Optional[Combatente]: ...

    def listar(
        self, combatente_id: int, classe: Optional[str] = None, favorita: Optional[bool] = None
    ) -> List[GrimorioMagia]: ...

    def listar_paginado(
        self,
        combatente_id: int,
        *,
        nome: Optional[str] = None,
        nivel: Optional[int] = None,
        escola: Optional[str] = None,
        componentes: Optional[str] = None,
        magia_ids: Optional[List[int]] = None,
        classe: Optional[str] = None,
        favorita: Optional[bool] = None,
        skip: int = 0,
        limit: Optional[int] = None,
    ) -> Tuple[int, List[GrimorioMagia]]: ...

    def listar_historico_troca(
        self, combatente_id: int, classe: Optional[str] = None, limit: int = 20
    ) -> List[GrimorioHistoricoTroca]: ...

    def listar_notificacoes(
        self,
        combatente_id: int,
        *,
        classe: Optional[str] = None,
        apenas_nao_lidas: bool = False,
        limit: int = 30,
    ) -> List[GrimorioNotificacao]: ...

    def get_notificacao(self, notificacao_id: int) -> Optional[GrimorioNotificacao]: ...

    def get_notificacao_aberta_por_tipo(
        self, combatente_id: int, classe: str, tipo: str
    ) -> Optional[GrimorioNotificacao]: ...

    def get_item(self, combatente_id: int, magia_id: int, classe: str) -> Optional[GrimorioMagia]: ...

    def create(self, item: GrimorioMagia) -> GrimorioMagia: ...

    def create_notificacao(self, item: GrimorioNotificacao) -> GrimorioNotificacao: ...

    def update(self, item: GrimorioMagia) -> GrimorioMagia: ...

    def update_notificacao(self, item: GrimorioNotificacao) -> GrimorioNotificacao: ...

    def delete(self, item: GrimorioMagia) -> None: ...

    def delete_notificacao(self, item: GrimorioNotificacao) -> None: ...

    def trocar_magia(
        self,
        *,
        item_antigo: GrimorioMagia,
        item_novo: GrimorioMagia,
        historico: GrimorioHistoricoTroca,
    ) -> GrimorioHistoricoTroca: ...
