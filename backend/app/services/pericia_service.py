"""[SHIM DE COMPATIBILIDADE] app.services.pericia_service

Re-exporta `PericiaService` de `app.games.dnd35.services.pericia_service`.
"""

from app.games.dnd35.services.pericia_service import PericiaService

__all__ = ["PericiaService"]
