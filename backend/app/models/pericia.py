"""[SHIM DE COMPATIBILIDADE] app.models.pericia

Re-exporta modelos de `app.games.dnd35.models.pericia`.
"""

from app.games.dnd35.models.pericia import (
    AtributoEnum,
    Pericia,
    PericiaClasse,
    PericiaJogador,
    TipoPericiaEnum,
)

__all__ = [
    "AtributoEnum",
    "TipoPericiaEnum",
    "Pericia",
    "PericiaClasse",
    "PericiaJogador",
]
