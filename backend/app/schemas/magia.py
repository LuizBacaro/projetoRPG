"""[SHIM DE COMPATIBILIDADE] app.schemas.magia

Re-exporta schemas de `app.games.dnd35.schemas.magia`.
"""

from app.games.dnd35.schemas.magia import (
    MagiaBase,
    MagiaClasseNivel,
    MagiaClasseNivelResponse,
    MagiaCreate,
    MagiaFiltro,
    MagiaHistoricoResponse,
    MagiaImportConfirmRequest,
    MagiaImportConfirmResponse,
    MagiaImportErro,
    MagiaImportPreviewItem,
    MagiaImportPreviewResponse,
    MagiaResponse,
    MagiaUpdate,
)

__all__ = [
    "MagiaClasseNivel",
    "MagiaClasseNivelResponse",
    "MagiaBase",
    "MagiaCreate",
    "MagiaUpdate",
    "MagiaResponse",
    "MagiaFiltro",
    "MagiaImportErro",
    "MagiaImportPreviewItem",
    "MagiaImportPreviewResponse",
    "MagiaImportConfirmRequest",
    "MagiaImportConfirmResponse",
    "MagiaHistoricoResponse",
]
