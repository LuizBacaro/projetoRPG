"""[SHIM DE COMPATIBILIDADE] app.core.classes_tables_catalog

Re-exporta o catálogo de `app.games.dnd35.catalogs.classes_tables_catalog`.
"""

from app.games.dnd35.catalogs.classes_tables_catalog import (
    initialize_classes_tables_catalog,
    load_classes_tables_catalog,
)

__all__ = [
    "load_classes_tables_catalog",
    "initialize_classes_tables_catalog",
]
