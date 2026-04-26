"""
[SHIM DE COMPATIBILIDADE] app.api.v1.divindades_custom

O router real vive em `app.games.dnd35.api.v1.divindades_custom`. Este
arquivo apenas re-exporta `router` para que `app/main.py` continue com:

    from .api.v1 import divindades_custom
    app.include_router(divindades_custom.router, ...)

Quando o registro de routers em main.py for atualizado para apontar
direto para o pacote do jogo, este shim pode ser removido.
"""
from ...games.dnd35.api.v1.divindades_custom import router

__all__ = ["router"]
