"""[SHIM DE COMPATIBILIDADE] app.models.magia

Re-exporta modelos de `app.games.dnd35.models.magia`.
"""

from app.games.dnd35.models.magia import Magia, MagiaClasse, MagiaHistorico

__all__ = ["Magia", "MagiaClasse", "MagiaHistorico"]
