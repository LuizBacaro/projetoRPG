"""[SHIM DE COMPATIBILIDADE] app.repositories.magia_repository

Re-exporta `MagiaRepository` de `app.games.dnd35.repositories.magia_repository`.
"""

from app.games.dnd35.repositories.magia_repository import MagiaRepository

__all__ = ["MagiaRepository"]
