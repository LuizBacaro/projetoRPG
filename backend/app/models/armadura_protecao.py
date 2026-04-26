"""[SHIM DE COMPATIBILIDADE] app.models.armadura_protecao

Re-exporta modelos de `app.games.dnd35.models.armadura_protecao`.
"""

from app.games.dnd35.models.armadura_protecao import ArmaduraProtecao, ArmaduraProtecaoJogador

__all__ = ["ArmaduraProtecao", "ArmaduraProtecaoJogador"]
