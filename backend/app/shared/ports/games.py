"""Contratos estruturais (Protocol) para catálogo de jogos e memberships (hub)."""

from __future__ import annotations

from typing import List, Optional, Protocol, Tuple

from sqlalchemy.orm import Session

from app.shared.models.game import Game, UserGameMembership
from app.shared.models.usuario import Usuario


class GameRepositoryProtocol(Protocol):
    """Superfície usada por `GameService` para o catálogo global de jogos."""

    db: Session

    def listar_disponiveis(self) -> List[Game]: ...

    def get_by_slug(self, slug: str) -> Optional[Game]: ...

    def get_by_id(self, game_id: int) -> Optional[Game]: ...


class UserGameMembershipRepositoryProtocol(Protocol):
    """Superfície usada por `GameService` para vínculos usuário–jogo."""

    db: Session

    def listar_por_usuario(
        self, usuario_id: int
    ) -> List[Tuple[UserGameMembership, Game]]: ...

    def buscar_por_usuario_e_slug(
        self, usuario_id: int, slug: str
    ) -> Optional[Tuple[UserGameMembership, Game]]: ...

    def criar(self, membership: UserGameMembership) -> UserGameMembership: ...

    def listar_memberships_de_jogo(
        self, game_id: int
    ) -> List[Tuple[UserGameMembership, Usuario]]: ...

    def get_by_id(self, membership_id: int) -> Optional[UserGameMembership]: ...

    def buscar_por_usuario_e_game_id(
        self, usuario_id: int, game_id: int
    ) -> Optional[UserGameMembership]: ...

    def atualizar(self, membership: UserGameMembership) -> UserGameMembership: ...

    def deletar(self, membership: UserGameMembership) -> None: ...
