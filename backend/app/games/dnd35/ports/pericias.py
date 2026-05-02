"""Contratos estruturais (Protocol) para `PericiaService` e repositórios de perícia."""

from __future__ import annotations

from typing import Dict, List, Optional, Protocol

from app.games.dnd35.models.pericia import Pericia, PericiaJogador
from app.games.dnd35.schemas.pericia import (
    PericiaCreate,
    PericiaJogadorUpdate,
    PericiaUpdate,
)


class PericiaCatalogRestoreProtocol(Protocol):
    """Superfície mínima para restauração de perícia soft-deletada."""

    def restaurar_pericia(self, db_pericia: Pericia, pericia: PericiaCreate) -> Pericia: ...


class PericiaRepositoryProtocol(PericiaCatalogRestoreProtocol, Protocol):
    """Catálogo e custos — usado por `PericiaService`."""

    def criar_pericia(self, pericia: PericiaCreate) -> Pericia: ...

    def obter_pericia(self, pericia_id: int) -> Optional[Pericia]: ...

    def obter_pericia_por_nome(self, nome: str) -> Optional[Pericia]: ...

    def listar_pericias(self, skip: int = 0, limit: int = 100) -> List[Pericia]: ...

    def listar_pericias_por_atributo(self, atributo: str) -> List[Pericia]: ...

    def listar_pericias_por_classe(self, classe_nome: str) -> List[Pericia]: ...

    def atualizar_pericia(
        self, pericia_id: int, pericia: PericiaUpdate
    ) -> Optional[Pericia]: ...

    def deletar_pericia(self, pericia_id: int) -> bool: ...

    def obter_custo_pericia(self, pericia_id: int, classe_nome: str) -> int: ...

    def obter_custos_pericias(
        self, pericia_ids: List[int], classe_nome: str
    ) -> Dict[int, int]: ...


class PericiaJogadorRepositoryProtocol(Protocol):
    """Persistência de vínculos combatente ↔ perícia — usado por `PericiaService`."""

    def obter_pericia_jogador(self, pericia_jogador_id: int) -> Optional[PericiaJogador]: ...

    def obter_pericia_jogador_por_ids(
        self, combatente_id: int, pericia_id: int
    ) -> Optional[PericiaJogador]: ...

    def listar_pericias_combatente_com_pericia(
        self, combatente_id: int
    ) -> List[PericiaJogador]: ...

    def persistir_novo_vinculo(self, row: PericiaJogador) -> PericiaJogador: ...

    def atualizar_pericia_jogador(
        self, pericia_jogador_id: int, pericia: PericiaJogadorUpdate
    ) -> Optional[PericiaJogador]: ...

    def deletar_pericia_jogador(self, pericia_jogador_id: int) -> bool: ...
