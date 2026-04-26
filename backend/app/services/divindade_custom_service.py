"""
[SHIM DE COMPATIBILIDADE] app.services.divindade_custom_service

O service real vive em
`app.games.dnd35.services.divindade_custom_service`. Mantido aqui apenas
para preservar `from ..services.divindade_custom_service import ...`
em chamadas legadas (ex.: api/v1/magias.py, services/combatente_service.py).
"""
from ..games.dnd35.services.divindade_custom_service import (
    DivindadeCustomService,
    TENDENCIAS_VALIDAS,
    build_divindade_custom_service,
)

__all__ = [
    "DivindadeCustomService",
    "TENDENCIAS_VALIDAS",
    "build_divindade_custom_service",
]
