"""[SHIM DE COMPATIBILIDADE] app.api.v1.magias

Re-exporta o router de `app.games.dnd35.api.v1.magias`.
"""

from app.games.dnd35.api.v1.magias import router

__all__ = ["router"]
