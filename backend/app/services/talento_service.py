"""[SHIM DE COMPATIBILIDADE] app.services.talento_service

Re-exporta `TalentoService` de `app.games.dnd35.services.talento_service`.
"""

from app.games.dnd35.services.talento_service import TalentoService

__all__ = ["TalentoService"]
