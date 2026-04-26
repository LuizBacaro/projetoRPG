"""[SHIM DE COMPATIBILIDADE] app.core.talentos_catalog_seed

Re-exporta o catálogo/seed de talentos LdJ de
`app.games.dnd35.catalogs.talentos_catalog_seed`.
"""

from app.games.dnd35.catalogs.talentos_catalog_seed import (
    MAPEAMENTO_SEED_PARA_JSON,
    aplicar_mapeamento_seed_antigo,
    default_json_path,
    desativar_talentos_fora_do_catalogo,
    load_rows_from_json,
    nomes_catalogo,
    seed_catalogo_inicial_vazio,
    sincronizar_catalogo_talentos_desde_json,
    upsert_talentos_from_rows,
)

__all__ = [
    "MAPEAMENTO_SEED_PARA_JSON",
    "aplicar_mapeamento_seed_antigo",
    "default_json_path",
    "desativar_talentos_fora_do_catalogo",
    "load_rows_from_json",
    "nomes_catalogo",
    "seed_catalogo_inicial_vazio",
    "sincronizar_catalogo_talentos_desde_json",
    "upsert_talentos_from_rows",
]
