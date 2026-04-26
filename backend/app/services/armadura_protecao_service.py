"""[SHIM DE COMPATIBILIDADE] app.services.armadura_protecao_service

Re-exporta `ArmaduraProtecaoService` de
`app.games.dnd35.services.armadura_protecao_service`.
"""

from app.games.dnd35.services.armadura_protecao_service import ArmaduraProtecaoService

__all__ = ["ArmaduraProtecaoService"]
