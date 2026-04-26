"""[SHIM DE COMPATIBILIDADE] app.repositories.ataque_repository

Re-exporta `AtaqueRepository` de `app.games.dnd35.repositories.ataque_repository`.
"""

from app.games.dnd35.repositories.ataque_repository import AtaqueRepository

__all__ = ["AtaqueRepository"]
