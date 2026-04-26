"""[SHIM DE COMPATIBILIDADE] app.repositories.combatente_repository

Re-exporta `CombatenteRepository` de
`app.games.dnd35.repositories.combatente_repository`.
"""

from app.games.dnd35.repositories.combatente_repository import CombatenteRepository

__all__ = ["CombatenteRepository"]
