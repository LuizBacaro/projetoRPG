"""
Metadados dos catálogos D&D 5E embutidos no Arena.

Ao regenerar dados a partir do upstream, atualize DND5E_DATABASE_VERSION e o changelog do PR.
"""

# Tag de referência do repositório 5e-bits/5e-database (OGL).
# Não implica que todo o JSON upstream está no repo — apenas a linha de base da última sincronização.
DND5E_DATABASE_VERSION = "v5.7.0"

# Origem documental dos módulos Python em app/games/dnd5e/data/
CATALOGO_SOURCES = {
    "racas": "5e-database + curadoria PT",
    "classes": "5e-database + curadoria PT",
    "magias": "foundry_spells + spell_i18n + magias_catalogo (subconjunto PHB)",
    "equipamento": "equipamento_catalogo.py (subconjunto)",
    "antecedentes": "antecedentes_catalogo.py",
    "feats": "feats_catalogo.py",
}
