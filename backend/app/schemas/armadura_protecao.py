"""[SHIM DE COMPATIBILIDADE] app.schemas.armadura_protecao

Re-exporta schemas de `app.games.dnd35.schemas.armadura_protecao`.
"""

from app.games.dnd35.schemas.armadura_protecao import (
    ArmaduraProtecaoBase,
    ArmaduraProtecaoCreate,
    ArmaduraProtecaoJogadorCreate,
    ArmaduraProtecaoJogadorListResponse,
    ArmaduraProtecaoResponse,
    BonusCaResponse,
)

__all__ = [
    "ArmaduraProtecaoBase",
    "ArmaduraProtecaoCreate",
    "ArmaduraProtecaoJogadorCreate",
    "ArmaduraProtecaoJogadorListResponse",
    "ArmaduraProtecaoResponse",
    "BonusCaResponse",
]
