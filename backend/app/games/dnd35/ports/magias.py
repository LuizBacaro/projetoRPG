"""Contrato estrutural (Protocol) para `MagiaRepository` / `MagiaService` (+ uso no grimório)."""

from __future__ import annotations

from typing import Any, List, Optional, Protocol, Tuple

from sqlalchemy.orm import Session

from app.games.dnd35.models.magia import Magia, MagiaHistorico


class MagiaRepositoryProtocol(Protocol):
    """Superfície usada por `MagiaService` e parcialmente por `GrimorioService`."""

    db: Session

    def listar_paginado(
        self,
        *,
        classe: Optional[str],
        nivel: Optional[int],
        escola: Optional[str],
        nome: Optional[str],
        componentes: Optional[str],
        dominio: Optional[str],
        ativo: Optional[bool],
        sort_by: Optional[str],
        sort_dir: Optional[str],
        skip: int,
        limit: int,
    ) -> Tuple[int, List[Magia]]: ...

    def listar_classes(self) -> List[str]: ...

    def get_by_id(self, entity_id: int) -> Optional[Magia]: ...

    def get_by_nome(self, nome: str) -> Optional[Magia]: ...

    def create(self, magia: Magia) -> Magia: ...

    def replace_classes(self, magia: Magia, classes_niveis: List[dict]) -> None: ...

    def save(self, magia: Magia) -> Magia: ...

    def registrar_historico(
        self,
        *,
        magia_id: int | None,
        usuario_id: int | None,
        acao: str,
        dados_anteriores: dict | None,
        dados_novos: dict | None,
    ) -> MagiaHistorico: ...

    def has_dependencias(self, magia_id: int) -> bool: ...

    def listar_historico(self, magia_id: int, *, limit: int = 50) -> List[MagiaHistorico]: ...


class MagiaCriacaoParaImportProtocol(Protocol):
    """Superfície usada por `MagiaImportService` (criação em lote a partir de Excel)."""

    def criar(self, payload: Any, *, usuario_id: int | None = None) -> Magia: ...
