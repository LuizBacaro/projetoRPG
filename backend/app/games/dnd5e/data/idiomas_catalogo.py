"""Catálogo de idiomas D&D 5E (PHB Cap. 4 / Apêndice)."""

from __future__ import annotations

from typing import Any, Dict, List

IDIOMAS_CATALOGO: List[Dict[str, Any]] = [
    {"slug": "comum", "nome": "Comum", "tipo": "padrao"},
    {"slug": "anao", "nome": "Anão", "tipo": "padrao"},
    {"slug": "elfico", "nome": "Élfico", "tipo": "padrao"},
    {"slug": "gigante", "nome": "Gigante", "tipo": "padrao"},
    {"slug": "gnomo", "nome": "Gnomo", "tipo": "padrao"},
    {"slug": "goblin", "nome": "Goblin", "tipo": "padrao"},
    {"slug": "halfling", "nome": "Halfling", "tipo": "padrao"},
    {"slug": "orc", "nome": "Orc", "tipo": "padrao"},
    {"slug": "abissal", "nome": "Abissal", "tipo": "exotico"},
    {"slug": "celestial", "nome": "Celestial", "tipo": "exotico"},
    {"slug": "draconico", "nome": "Dracônico", "tipo": "exotico"},
    {"slug": "infernal", "nome": "Infernal", "tipo": "exotico"},
    {"slug": "primordial", "nome": "Primordial", "tipo": "exotico"},
    {"slug": "silvano", "nome": "Silvano", "tipo": "exotico"},
    {"slug": "subcomum", "nome": "Subcomum", "tipo": "exotico"},
]

IDIOMAS_SLUGS_VALIDOS = frozenset(row["slug"] for row in IDIOMAS_CATALOGO)
