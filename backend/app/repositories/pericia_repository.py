"""[SHIM DE COMPATIBILIDADE] app.repositories.pericia_repository

Re-exporta de `app.games.dnd35.repositories.pericia_repository`.
"""

from app.games.dnd35.repositories.pericia_repository import (
    PericiaJogadorRepository,
    PericiaRepository,
)

__all__ = ["PericiaRepository", "PericiaJogadorRepository"]
