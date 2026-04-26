"""[SHIM DE COMPATIBILIDADE] app.schemas.grimorio

Re-exporta schemas de `app.games.dnd35.schemas.grimorio`.
"""

from app.games.dnd35.schemas.grimorio import (
    GrimorioDiagnosticoMagiaResponse,
    GrimorioDiagnosticoResponse,
    GrimorioHistoricoTrocaResponse,
    GrimorioMagiaCreate,
    GrimorioMagiaResponse,
    GrimorioMagiaUpdate,
    GrimorioNotificacaoResponse,
    GrimorioNotificacaoUpdate,
    GrimorioTrocaRequest,
    GrimorioTrocaResponse,
)

__all__ = [
    "GrimorioMagiaCreate",
    "GrimorioMagiaUpdate",
    "GrimorioMagiaResponse",
    "GrimorioTrocaRequest",
    "GrimorioTrocaResponse",
    "GrimorioHistoricoTrocaResponse",
    "GrimorioNotificacaoResponse",
    "GrimorioNotificacaoUpdate",
    "GrimorioDiagnosticoMagiaResponse",
    "GrimorioDiagnosticoResponse",
]
