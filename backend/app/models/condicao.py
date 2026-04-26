"""[SHIM DE COMPATIBILIDADE] app.models.condicao

Re-exporta `Condicao` de `app.games.dnd35.models.condicao`.
"""

from app.games.dnd35.models.condicao import Condicao

__all__ = ["Condicao"]
