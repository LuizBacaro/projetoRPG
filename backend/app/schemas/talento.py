"""[SHIM DE COMPATIBILIDADE] app.schemas.talento

Re-exporta os schemas de talento de `app.games.dnd35.schemas.talento`.
"""

from app.games.dnd35.schemas.talento import (
    TalentoBase,
    TalentoCreate,
    TalentoJogadorBase,
    TalentoJogadorCreate,
    TalentoJogadorListResponse,
    TalentoJogadorResponse,
    TalentoResponse,
)

__all__ = [
    "TalentoBase",
    "TalentoCreate",
    "TalentoResponse",
    "TalentoJogadorBase",
    "TalentoJogadorCreate",
    "TalentoJogadorResponse",
    "TalentoJogadorListResponse",
]
