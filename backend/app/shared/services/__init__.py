"""Services canônicos do Auth Hub em `app.shared.services`."""

from .usuario_service import UsuarioService
from .game_service import GameService

__all__ = ["UsuarioService", "GameService"]
