"""[SHIM DE COMPATIBILIDADE] app.api.v1.ataques

Re-exporta o router de `app.games.dnd35.api.v1.ataques`.
"""

from app.games.dnd35.api.v1.ataques import router

__all__ = ["router"]
