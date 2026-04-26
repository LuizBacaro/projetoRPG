"""[SHIM DE COMPATIBILIDADE] app.api.v1.tabelas_classes

Re-exporta o router de `app.games.dnd35.api.v1.tabelas_classes`.
"""

from app.games.dnd35.api.v1.tabelas_classes import router

__all__ = ["router"]
