"""[SHIM DE COMPATIBILIDADE] app.repositories.grimorio_repository

Re-exporta `GrimorioRepository` de
`app.games.dnd35.repositories.grimorio_repository`.
"""

from app.games.dnd35.repositories.grimorio_repository import GrimorioRepository

__all__ = ["GrimorioRepository"]
