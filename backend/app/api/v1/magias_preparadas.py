"""[SHIM DE COMPATIBILIDADE] app.api.v1.magias_preparadas

Re-exporta o router de `app.games.dnd35.api.v1.magias_preparadas`.
"""

from app.games.dnd35.api.v1.magias_preparadas import router

__all__ = ["router"]
