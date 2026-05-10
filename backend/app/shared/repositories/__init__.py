"""Repositórios canônicos do Auth Hub em `app.shared.repositories`."""

from .game_repository import GameRepository, UserGameMembershipRepository
from .usuario_repository import UsuarioRepository

__all__ = [
    "UsuarioRepository",
    "GameRepository",
    "UserGameMembershipRepository",
]
