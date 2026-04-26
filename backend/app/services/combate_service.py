"""[SHIM DE COMPATIBILIDADE] app.services.combate_service

Re-exporta `CombateService` de `app.games.dnd35.services.combate_service`.
"""

from app.games.dnd35.services.combate_service import CombateService

__all__ = ["CombateService"]
