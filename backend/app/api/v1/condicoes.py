"""[SHIM DE COMPATIBILIDADE] app.api.v1.condicoes

Re-exporta o router de `app.games.dnd35.api.v1.condicoes`.
"""

from app.games.dnd35.api.v1.condicoes import router

__all__ = ["router"]
