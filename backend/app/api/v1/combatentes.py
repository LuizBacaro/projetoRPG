"""[SHIM DE COMPATIBILIDADE] app.api.v1.combatentes

Re-exporta o router de `app.games.dnd35.api.v1.combatentes`.
"""

from app.games.dnd35.api.v1.combatentes import router

__all__ = ["router"]
