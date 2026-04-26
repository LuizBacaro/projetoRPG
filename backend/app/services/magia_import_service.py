"""[SHIM DE COMPATIBILIDADE] app.services.magia_import_service

Re-exporta `MagiaImportService` de
`app.games.dnd35.services.magia_import_service`.
"""

from app.games.dnd35.services.magia_import_service import MagiaImportService

__all__ = ["MagiaImportService"]
