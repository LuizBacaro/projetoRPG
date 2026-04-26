"""[SHIM DE COMPATIBILIDADE] app.services.condicao_service

Re-exporta `CondicaoService` e `CONDICOES_SEED` de
`app.games.dnd35.services.condicao_service`.
"""

from app.games.dnd35.services.condicao_service import CONDICOES_SEED, CondicaoService

__all__ = ["CONDICOES_SEED", "CondicaoService"]
