"""[SHIM DE COMPATIBILIDADE] app.services.tabelas_classes_service

Re-exporta `TabelasClassesService` de
`app.games.dnd35.services.tabelas_classes_service`.
"""

from app.games.dnd35.services.tabelas_classes_service import TabelasClassesService

__all__ = ["TabelasClassesService"]
