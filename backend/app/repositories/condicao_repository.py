"""[SHIM DE COMPATIBILIDADE] app.repositories.condicao_repository

Re-exporta `CondicaoRepository` de `app.games.dnd35.repositories.condicao_repository`.
"""

from app.games.dnd35.repositories.condicao_repository import CondicaoRepository

__all__ = ["CondicaoRepository"]
