"""[SHIM DE COMPATIBILIDADE] app.api.v1.armaduras_protecao

Re-exporta o router de `app.games.dnd35.api.v1.armaduras_protecao`.
"""

from app.games.dnd35.api.v1.armaduras_protecao import router

__all__ = ["router"]
