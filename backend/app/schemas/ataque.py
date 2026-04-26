"""[SHIM DE COMPATIBILIDADE] app.schemas.ataque

Re-exporta schemas de `app.games.dnd35.schemas.ataque`.
"""

from app.games.dnd35.schemas.ataque import (
    AtaqueBase,
    AtaqueCreate,
    AtaqueResponse,
    AtaquesBulkRequest,
    DescansoRequest,
    MagiaPreparadaCreate,
    MagiaPreparadaResponse,
    MagiaSlotBase,
    MagiaSlotCreate,
    MagiaSlotResponse,
    MagiaSlotUpdate,
    MagiasBulkRequest,
)

__all__ = [
    "AtaqueBase",
    "AtaqueCreate",
    "AtaqueResponse",
    "AtaquesBulkRequest",
    "DescansoRequest",
    "MagiaPreparadaCreate",
    "MagiaPreparadaResponse",
    "MagiaSlotBase",
    "MagiaSlotCreate",
    "MagiaSlotResponse",
    "MagiaSlotUpdate",
    "MagiasBulkRequest",
]
