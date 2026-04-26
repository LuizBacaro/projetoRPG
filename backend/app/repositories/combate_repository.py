"""[SHIM DE COMPATIBILIDADE] app.repositories.combate_repository

Re-exporta `CombateRepository` de `app.games.dnd35.repositories.combate_repository`.
"""

from app.games.dnd35.repositories.combate_repository import CombateRepository

__all__ = ["CombateRepository"]
