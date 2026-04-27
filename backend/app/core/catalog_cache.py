"""[SHIM DE COMPATIBILIDADE] app.core.catalog_cache

Re-exporta cache canônico de `app.shared.core.catalog_cache` enquanto o hub
é consolidado em `app/shared/`.
"""

from app.shared.core.catalog_cache import CatalogCache, catalog_cache, make_cache_key

__all__ = ["CatalogCache", "catalog_cache", "make_cache_key"]
