"""Services canônicos do Auth Hub em `app.shared.services`."""

from .game_service import GameService
from .usuario_service import UsuarioService

__all__ = ["UsuarioService", "GameService"]
