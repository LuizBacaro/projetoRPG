"""[SHIM DE COMPATIBILIDADE] app.models.combate

Re-exporta modelos de `app.games.dnd35.models.combate`.
"""

from app.games.dnd35.models.combate import Combate, CombateHistorico

__all__ = ["Combate", "CombateHistorico"]
