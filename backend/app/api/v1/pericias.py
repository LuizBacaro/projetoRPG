"""[SHIM DE COMPATIBILIDADE] app.api.v1.pericias

Re-exporta o router de `app.games.dnd35.api.v1.pericias`.
"""

from app.games.dnd35.api.v1.pericias import router

__all__ = ["router"]
