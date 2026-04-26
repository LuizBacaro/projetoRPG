"""[SHIM DE COMPATIBILIDADE] app.api.v1.combate

Re-exporta o router de `app.games.dnd35.api.v1.combate` e os `Depends`
usados pelo router (testes e overrides importam deste módulo).
"""

from app.core.dependencies import get_combate_service, get_condicao_service
from app.core.deps import get_usuario_atual
from app.games.dnd35.api.v1.combate import router

__all__ = [
    "router",
    "get_combate_service",
    "get_condicao_service",
    "get_usuario_atual",
]
