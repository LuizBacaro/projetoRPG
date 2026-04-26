"""[SHIM DE COMPATIBILIDADE] app.services.magia_service

Re-exporta `MagiaService` de `app.games.dnd35.services.magia_service`.
"""

from app.games.dnd35.services.magia_service import DOMINIOS_FIXOS, MagiaService

__all__ = ["MagiaService", "DOMINIOS_FIXOS"]
