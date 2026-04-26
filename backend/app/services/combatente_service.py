"""[SHIM DE COMPATIBILIDADE] app.services.combatente_service

Re-exporta `CombatenteService` de `app.games.dnd35.services.combatente_service`.
"""

from app.games.dnd35.services.combatente_service import CombatenteService

__all__ = ["CombatenteService"]
