"""[SHIM DE COMPATIBILIDADE] app.schemas.condicao

Re-exporta schemas de `app.games.dnd35.schemas.condicao`.
"""

from app.games.dnd35.schemas.condicao import (
    AplicarCondicaoMassaRequest,
    AplicarCondicaoMassaResponse,
    AplicarCondicaoRequest,
    CondicaoAtivaResponse,
    CondicaoResponse,
    RemoverCondicaoRequest,
)

__all__ = [
    "AplicarCondicaoMassaRequest",
    "AplicarCondicaoMassaResponse",
    "AplicarCondicaoRequest",
    "CondicaoAtivaResponse",
    "CondicaoResponse",
    "RemoverCondicaoRequest",
]
