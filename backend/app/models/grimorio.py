"""[SHIM DE COMPATIBILIDADE] app.models.grimorio

Re-exporta modelos de `app.games.dnd35.models.grimorio`.
"""

from app.games.dnd35.models.grimorio import (
    GrimorioHistoricoTroca,
    GrimorioMagia,
    GrimorioNotificacao,
)

__all__ = ["GrimorioMagia", "GrimorioHistoricoTroca", "GrimorioNotificacao"]
