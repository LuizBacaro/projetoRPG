"""[SHIM DE COMPATIBILIDADE] app.models.combatente_condicao

Re-exporta `CombatenteCondicao` de `app.games.dnd35.models.combatente_condicao`.
"""

from app.games.dnd35.models.combatente_condicao import CombatenteCondicao

__all__ = ["CombatenteCondicao"]
