"""[SHIM DE COMPATIBILIDADE] app.api.v1.talentos

Re-exporta o router de `app.games.dnd35.api.v1.talentos`.
"""

from app.games.dnd35.api.v1.talentos import router

__all__ = ["router"]
