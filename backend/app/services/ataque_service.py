"""[SHIM DE COMPATIBILIDADE] app.services.ataque_service

Re-exporta `AtaqueService` de `app.games.dnd35.services.ataque_service`.
"""

from app.games.dnd35.services.ataque_service import AtaqueService

__all__ = ["AtaqueService"]
