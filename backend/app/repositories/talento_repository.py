"""[SHIM DE COMPATIBILIDADE] app.repositories.talento_repository

Re-exporta os repositórios de `app.games.dnd35.repositories.talento_repository`.
"""

from app.games.dnd35.repositories.talento_repository import (
    TalentoJogadorRepository,
    TalentoRepository,
)

__all__ = ["TalentoRepository", "TalentoJogadorRepository"]
