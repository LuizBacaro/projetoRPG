"""[SHIM DE COMPATIBILIDADE] app.api.v1.combate

Re-exporta o router de `app.games.dnd35.api.v1.combate`.
"""

from app.games.dnd35.api.v1.combate import router

__all__ = ["router"]
