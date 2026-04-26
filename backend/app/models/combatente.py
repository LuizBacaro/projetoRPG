"""[SHIM DE COMPATIBILIDADE] app.models.combatente

Re-exporta `Combatente` de `app.games.dnd35.models.combatente`.
"""

from app.games.dnd35.models.combatente import Combatente

__all__ = ["Combatente"]
