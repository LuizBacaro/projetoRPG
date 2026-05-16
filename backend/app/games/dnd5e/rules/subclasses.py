"""Subclasses D&D 5E — catálogo por classe."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.dnd5e.data.subclasses_catalogo import SUBCLASSES_CATALOGO


def listar_subclasses(classe_slug: Optional[str] = None) -> List[Dict[str, Any]]:
    key = (classe_slug or "").strip().lower()
    rows = SUBCLASSES_CATALOGO
    if key:
        rows = [r for r in rows if r.get("classe_slug") == key]
    return [dict(r) for r in rows]


def subclasse_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    key = (slug or "").strip().lower()
    for row in SUBCLASSES_CATALOGO:
        if row.get("slug") == key:
            return dict(row)
    return None


def validar_subclasse_para_classe(
    subclasse_slug: Optional[str],
    classe_slug: str,
    nivel: int,
) -> Optional[Dict[str, Any]]:
    if not subclasse_slug:
        return None
    sub = subclasse_por_slug(subclasse_slug)
    if sub is None:
        raise ValueError(f"Subclasse inválida: {subclasse_slug}")
    if sub.get("classe_slug") != (classe_slug or "").strip().lower():
        raise ValueError("Subclasse não pertence à classe selecionada")
    if nivel < int(sub.get("nivel_escolha", 3)):
        raise ValueError(
            f"Subclasse disponível a partir do nível {sub.get('nivel_escolha')}"
        )
    return sub
