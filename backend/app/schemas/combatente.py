"""[SHIM DE COMPATIBILIDADE] app.schemas.combatente

Re-exporta schemas de `app.games.dnd35.schemas.combatente`.
"""

from app.games.dnd35.schemas.combatente import (
    CombatenteBase,
    CombatenteCreate,
    CombatenteResponse,
    CombatenteUpdate,
    DanoCuraMassaRequest,
    DanoCuraMassaResponse,
    DanoCuraRequest,
    DanoCuraResponse,
    DanoRequest,
    HabilidadeEspecialEnriquecida,
    HabilidadesEspeciaisNivel,
    HPUpdateRequest,
    IniciativaUpdateRequest,
)

__all__ = [
    "CombatenteBase",
    "CombatenteCreate",
    "CombatenteResponse",
    "CombatenteUpdate",
    "DanoCuraMassaRequest",
    "DanoCuraMassaResponse",
    "DanoCuraRequest",
    "DanoCuraResponse",
    "DanoRequest",
    "HabilidadeEspecialEnriquecida",
    "HabilidadesEspeciaisNivel",
    "HPUpdateRequest",
    "IniciativaUpdateRequest",
]
