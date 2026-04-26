"""[SHIM DE COMPATIBILIDADE] app.repositories.armadura_protecao_repository

Re-exporta repositórios de `app.games.dnd35.repositories.armadura_protecao_repository`.
"""

from app.games.dnd35.repositories.armadura_protecao_repository import (
    ArmaduraProtecaoJogadorRepository,
    ArmaduraProtecaoRepository,
)

__all__ = ["ArmaduraProtecaoRepository", "ArmaduraProtecaoJogadorRepository"]
