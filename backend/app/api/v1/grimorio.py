"""[SHIM DE COMPATIBILIDADE] app.api.v1.grimorio

Re-exporta o router de `app.games.dnd35.api.v1.grimorio`.
"""

from app.games.dnd35.api.v1.grimorio import router

__all__ = ["router"]
