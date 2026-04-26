"""[SHIM DE COMPATIBILIDADE] app.models.ataque

Re-exporta modelos de `app.games.dnd35.models.ataque`.
"""

from app.games.dnd35.models.ataque import Ataque, MagiaPreparada, MagiaSlot

__all__ = ["Ataque", "MagiaSlot", "MagiaPreparada"]
