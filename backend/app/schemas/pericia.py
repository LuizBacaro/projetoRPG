"""[SHIM DE COMPATIBILIDADE] app.schemas.pericia

Re-exporta schemas de `app.games.dnd35.schemas.pericia`.
"""

from app.games.dnd35.schemas.pericia import (
    AtributoEnum,
    PericiaBase,
    PericiaClasseResponse,
    PericiaCreate,
    PericiaJogadorBase,
    PericiaJogadorCreate,
    PericiaJogadorListResponse,
    PericiaJogadorResponse,
    PericiaJogadorUpdate,
    PericiaResponse,
    PericiaUpdate,
    TipoPericiaEnum,
)

__all__ = [
    "AtributoEnum",
    "TipoPericiaEnum",
    "PericiaBase",
    "PericiaCreate",
    "PericiaUpdate",
    "PericiaResponse",
    "PericiaClasseResponse",
    "PericiaJogadorBase",
    "PericiaJogadorCreate",
    "PericiaJogadorUpdate",
    "PericiaJogadorResponse",
    "PericiaJogadorListResponse",
]
