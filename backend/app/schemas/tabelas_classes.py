"""[SHIM DE COMPATIBILIDADE] app.schemas.tabelas_classes

Re-exporta schemas de `app.games.dnd35.schemas.tabelas_classes`.
"""

from app.games.dnd35.schemas.tabelas_classes import (
    TabelaClassesResponse,
    TabelasClassesListResponse,
)

__all__ = ["TabelaClassesResponse", "TabelasClassesListResponse"]
