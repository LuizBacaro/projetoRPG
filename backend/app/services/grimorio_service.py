"""[SHIM DE COMPATIBILIDADE] app.services.grimorio_service

Re-exporta `GrimorioService` de `app.games.dnd35.services.grimorio_service`.
"""

from app.games.dnd35.services.grimorio_service import GrimorioService

__all__ = ["GrimorioService"]
