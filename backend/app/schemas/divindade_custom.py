"""
[SHIM DE COMPATIBILIDADE] app.schemas.divindade_custom

Os schemas reais foram movidos para
`app.games.dnd35.schemas.divindade_custom` como parte da reorganização
multi-jogo. Este módulo apenas re-exporta para preservar imports legados.
"""
from ..games.dnd35.schemas.divindade_custom import (
    DivindadeCustomBase,
    DivindadeCustomCreate,
    DivindadeCustomResponse,
)

__all__ = [
    "DivindadeCustomBase",
    "DivindadeCustomCreate",
    "DivindadeCustomResponse",
]
