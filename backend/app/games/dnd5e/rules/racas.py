"""Raças D&D 5E — catálogo PHB para API/ficha."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.dnd5e.data.racas_catalogo import RACAS_CATALOGO

RACA_SLUGS_VALIDOS = frozenset(r["slug"] for r in RACAS_CATALOGO)


def lista_racas_catalogo() -> List[Dict[str, Any]]:
    """Lista as nove raças com bônus e traços resumidos."""
    return list(RACAS_CATALOGO)


def raca_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    key = (slug or "").strip().lower()
    for row in RACAS_CATALOGO:
        if row.get("slug") == key:
            return dict(row)
    return None
