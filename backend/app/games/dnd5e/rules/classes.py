"""Classes D&D 5E — catálogo e progressão por XP."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.dnd5e.data.classes_catalogo import (
    CLASSES_CATALOGO,
    NIVEIS_GANHO_FEAT,
    TABELA_XP_POR_NIVEL,
)
from app.games.dnd5e.data.classes_proficiencias import proficiencias_classe

CLASSE_SLUGS_VALIDOS = frozenset(c["slug"] for c in CLASSES_CATALOGO)


def lista_classes_catalogo() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for row in CLASSES_CATALOGO:
        merged = dict(row)
        merged.update(proficiencias_classe(row["slug"]))
        out.append(merged)
    return out


def tabela_xp_por_nivel() -> List[Dict[str, int]]:
    return list(TABELA_XP_POR_NIVEL)


def niveis_com_ganho_feat() -> List[int]:
    return list(NIVEIS_GANHO_FEAT)


def classe_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    key = (slug or "").strip().lower()
    for row in CLASSES_CATALOGO:
        if row.get("slug") == key:
            merged = dict(row)
            merged.update(proficiencias_classe(key))
            return merged
    return None


def nivel_por_xp(xp_total: int) -> int:
    """Nível efetivo dado XP acumulado (PHB)."""
    xp = max(0, int(xp_total))
    nivel = 1
    for row in TABELA_XP_POR_NIVEL:
        if xp >= row["xp_total"]:
            nivel = row["nivel"]
    return nivel


def xp_minima_por_nivel(nivel: int) -> int:
    """XP mínima acumulada para estar no nível informado (PHB)."""
    nivel_ef = max(1, min(20, int(nivel)))
    for row in TABELA_XP_POR_NIVEL:
        if row["nivel"] == nivel_ef:
            return int(row["xp_total"])
    return 0
