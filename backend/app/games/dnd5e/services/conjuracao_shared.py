"""Helpers partilhados — conjuração (evita import circular)."""

from __future__ import annotations

from typing import Optional

from app.games.dnd5e.data.spell_tables import (
    FULL_SPELL_LIST_PREPARED_CLASSES,
    KNOWN_CLASSES,
    KNOWN_SPELLS_FULL,
    KNOWN_SPELLS_HALF_CASTER,
    KNOWN_SPELLS_WARLOCK,
    PREPARED_CLASSES,
    PREPARED_FULL_CASTER_CLASSES,
    PREPARED_HALF_CASTER_CLASSES,
    SHORT_REST_RECOVER_ALL,
    magias_preparadas_max_full_caster,
    magias_preparadas_max_paladino,
)


def classe_slug_ficha(ficha: dict) -> str:
    return (ficha.get("classe_slug") or "").strip().lower()


def classe_prepara_magias(classe: str) -> bool:
    return classe in PREPARED_CLASSES


def modo_lista_conjuracao(classe: str) -> str:
    slug = (classe or "").strip().lower()
    if slug == "bruxo":
        return "bruxo"
    if slug in PREPARED_CLASSES:
        return "preparado"
    if slug in KNOWN_CLASSES:
        return "conhecido"
    return "nenhum"


def perfil_conjuracao_classe(
    classe: str,
    nivel: int,
    *,
    mod_habilidade: int = 0,
) -> dict:
    """Metadados PHB por classe (slots, modo de lista, teto de nível de magia)."""
    from app.games.dnd5e.rules.magia import (
        espacos_por_classe_nivel,
        habilidade_primaria_classe,
        max_nivel_magia_conjuravel,
    )

    slug = (classe or "").strip().lower()
    nivel = max(1, min(20, int(nivel)))
    return {
        "classe": slug,
        "nivel": nivel,
        "habilidade_primaria": habilidade_primaria_classe(slug),
        "modo_lista": modo_lista_conjuracao(slug),
        "max_nivel_magia": max_nivel_magia_conjuravel(slug, nivel),
        "recupera_slots_repouso_curto": slug in SHORT_REST_RECOVER_ALL,
        "espacos_por_nivel": espacos_por_classe_nivel(slug, nivel),
        "magias_conhecidas_max": magias_conhecidas_max(slug, nivel),
        "magias_preparadas_max": magias_preparadas_max(slug, nivel, mod_habilidade),
    }


def magias_conhecidas_max(classe: str, nivel: int) -> Optional[int]:
    if classe in PREPARED_CLASSES:
        return None
    if classe == "bruxo":
        return KNOWN_SPELLS_WARLOCK.get(nivel, 0)
    if classe == "patrulheiro":
        return KNOWN_SPELLS_HALF_CASTER.get(nivel, 0)
    return KNOWN_SPELLS_FULL.get(nivel, 0)


def magias_preparadas_max(
    classe: str, nivel: int, mod_habilidade: int
) -> Optional[int]:
    if classe in PREPARED_FULL_CASTER_CLASSES:
        return magias_preparadas_max_full_caster(mod_habilidade, nivel)
    if classe in PREPARED_HALF_CASTER_CLASSES:
        return magias_preparadas_max_paladino(mod_habilidade, nivel)
    return None


def contar_magias_preparadas_com_nivel(
    magia_ids: list[int], niveis_por_id: dict[int, int]
) -> int:
    """Truques (nível 0) não entram no limite PHB de magias preparadas."""
    total = 0
    for mid in magia_ids:
        if int(niveis_por_id.get(int(mid), 0)) >= 1:
            total += 1
    return total


def normalizar_magias_preparadas_qty(raw) -> dict[str, int]:
    """Mapa magia_id (str) → quantidade preparada (≥1)."""
    if not isinstance(raw, dict):
        return {}
    resultado: dict[str, int] = {}
    for chave, valor in raw.items():
        try:
            magia_id = int(chave)
            quantidade = int(valor)
        except (TypeError, ValueError):
            continue
        if magia_id < 1 or quantidade < 1:
            continue
        resultado[str(magia_id)] = quantidade
    return resultado


def somar_qty_preparadas_por_nivel(
    qty_map: dict[str, int], niveis_por_id: dict[int, int]
) -> dict[int, int]:
    totais: dict[int, int] = {}
    for chave, quantidade in (qty_map or {}).items():
        try:
            magia_id = int(chave)
        except (TypeError, ValueError):
            continue
        nivel = int(niveis_por_id.get(magia_id, 0))
        if nivel <= 0:
            continue
        totais[nivel] = totais.get(nivel, 0) + int(quantidade)
    return totais


def contar_magias_conhecidas_grimorio(itens) -> int:
    """Magias de nível ≥ 1 no grimório (truques não entram no limite PHB de conhecidas)."""
    total = 0
    for item in itens or []:
        magia = getattr(item, "magia", None)
        if magia is not None and int(magia.nivel or 0) >= 1:
            total += 1
    return total
