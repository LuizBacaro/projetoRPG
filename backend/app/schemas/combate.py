"""[SHIM DE COMPATIBILIDADE] app.schemas.combate

Re-exporta schemas de `app.games.dnd35.schemas.combate`.
"""

from app.games.dnd35.schemas.combate import (
    AplicarDanoRequest,
    CombateHistoricoListResponse,
    CombateHistoricoResponse,
    CombateResponse,
    IniciarCombateRequest,
)

__all__ = [
    "AplicarDanoRequest",
    "CombateHistoricoListResponse",
    "CombateHistoricoResponse",
    "CombateResponse",
    "IniciarCombateRequest",
]
