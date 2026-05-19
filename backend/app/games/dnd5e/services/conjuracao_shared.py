"""Helpers partilhados — conjuração (evita import circular)."""

from __future__ import annotations

from typing import Optional

from app.games.dnd5e.data.spell_tables import (
    KNOWN_SPELLS_FULL,
    KNOWN_SPELLS_HALF_CASTER,
    KNOWN_SPELLS_WARLOCK,
    PREPARED_CLASSES,
    PREPARED_FULL_CASTER_CLASSES,
    PREPARED_HALF_CASTER_CLASSES,
    magias_preparadas_max_full_caster,
    magias_preparadas_max_paladino,
)


def classe_slug_ficha(ficha: dict) -> str:
    return (ficha.get("classe_slug") or "").strip().lower()


def classe_prepara_magias(classe: str) -> bool:
    return classe in PREPARED_CLASSES


def magias_conhecidas_max(classe: str, nivel: int) -> Optional[int]:
    if classe in PREPARED_CLASSES:
        return None
    if classe == "bruxo":
        return KNOWN_SPELLS_WARLOCK.get(nivel, 0)
    if classe == "patrulheiro":
        return KNOWN_SPELLS_HALF_CASTER.get(nivel, 0)
    return KNOWN_SPELLS_FULL.get(nivel, 0)


def magias_preparadas_max(classe: str, nivel: int, mod_habilidade: int) -> Optional[int]:
    if classe in PREPARED_FULL_CASTER_CLASSES:
        return magias_preparadas_max_full_caster(mod_habilidade, nivel)
    if classe in PREPARED_HALF_CASTER_CLASSES:
        return magias_preparadas_max_paladino(mod_habilidade, nivel)
    return None


def contar_magias_conhecidas_grimorio(itens) -> int:
    """Magias de nível ≥ 1 no grimório (truques não entram no limite PHB de conhecidas)."""
    total = 0
    for item in itens or []:
        magia = getattr(item, "magia", None)
        if magia is not None and int(magia.nivel or 0) >= 1:
            total += 1
    return total
