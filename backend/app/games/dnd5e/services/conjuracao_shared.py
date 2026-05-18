"""Helpers partilhados — conjuração (evita import circular)."""

from __future__ import annotations

from typing import Optional

from app.games.dnd5e.data.spell_tables import (
    KNOWN_SPELLS_FULL,
    KNOWN_SPELLS_WARLOCK,
    PREPARED_CLASSES,
)


def classe_slug_ficha(ficha: dict) -> str:
    return (ficha.get("classe_slug") or "").strip().lower()


def magias_conhecidas_max(classe: str, nivel: int) -> Optional[int]:
    if classe in PREPARED_CLASSES:
        return None
    if classe == "bruxo":
        return KNOWN_SPELLS_WARLOCK.get(nivel, 0)
    return KNOWN_SPELLS_FULL.get(nivel, 0)
