"""Repositórios canônicos do Auth Hub em `app.shared.repositories`."""

from .usuario_repository import UsuarioRepository
from .game_repository import GameRepository, UserGameMembershipRepository

__all__ = [
    "UsuarioRepository",
    "GameRepository",
    "UserGameMembershipRepository",
]
