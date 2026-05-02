"""Contratos estruturais (Protocol) para catálogo de equipamentos e vínculo ao combatente."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Protocol

from app.games.dnd35.models.equipamento import Equipamento, EquipamentoJogador
from app.games.dnd35.schemas.equipamento import EquipamentoCreate, EquipamentoJogadorCreate


class EquipamentoCatalogProtocol(Protocol):
    """Catálogo global de equipamentos — usado por `EquipamentoService`."""

    def restaurar_equipamento(
        self, db_equipamento: Equipamento, equipamento: EquipamentoCreate
    ) -> Equipamento: ...

    def criar_equipamento(self, equipamento: EquipamentoCreate) -> Equipamento: ...

    def obter_equipamento(self, equipamento_id: int) -> Optional[Equipamento]: ...

    def listar_equipamentos(self, skip: int = 0, limit: int = 100) -> List[Equipamento]: ...

    def atualizar_equipamento(
        self, equipamento_id: int, equipamento_data: Dict[str, Any]
    ) -> Optional[Equipamento]: ...

    def deletar_equipamento(self, equipamento_id: int) -> bool: ...


class EquipamentoJogadorLinksProtocol(Protocol):
    """Vínculos combatente ↔ equipamento — usado por `EquipamentoService`."""

    def adicionar_equipamento(
        self, combatente_id: int, equipamento_jogador: EquipamentoJogadorCreate
    ) -> EquipamentoJogador: ...

    def obter_equipamentos_jogador_detalhado(self, combatente_id: int) -> List[dict]: ...

    def remover_equipamento(self, combatente_id: int, equipamento_id: int) -> bool: ...

    def atualizar_quantidade(
        self, combatente_id: int, equipamento_id: int, quantidade: int
    ) -> Optional[EquipamentoJogador]: ...
