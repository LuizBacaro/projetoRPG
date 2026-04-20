"""
Cálculo de Bônus Base de Ataque (BBA) para classes D&D.

Fonte primária: catálogo consolidado em `docs/dados/tabelas_classes_catalogo.json`.
Fallback: progressões padrão (boa/média/ruim) para manter robustez caso o catálogo
não esteja disponível no ambiente.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re

from .config import settings
from .text_utils import normalizar_classe

_TABLE_BY_CLASS: dict[str, int] = {
    "BARBARO": 3,
    "BARDO": 4,
    "CLERIGO": 6,
    "DRUIDA": 8,
    "FEITICEIRO": 9,
    "GUERREIRO": 11,
    "LADINO": 12,
    "MAGO": 13,
    "MONGE": 14,
    "PALADINO": 16,
    "RANGER": 17,
    "PATRULHEIRO": 17,
}

_PROGRESSION_BY_CLASS: dict[str, str] = {
    "BARBARO": "good",
    "BARDO": "medium",
    "CLERIGO": "medium",
    "DRUIDA": "medium",
    "FEITICEIRO": "poor",
    "GUERREIRO": "good",
    "LADINO": "medium",
    "MAGO": "poor",
    "MONGE": "medium",
    "PALADINO": "good",
    "RANGER": "good",
    "PATRULHEIRO": "good",
}

_SAVE_PROGRESSION_BY_CLASS: dict[str, tuple[str, str, str]] = {
    # (fortitude, reflexos, vontade)
    "BARBARO": ("good", "poor", "poor"),
    "BARDO": ("poor", "good", "good"),
    "CLERIGO": ("good", "poor", "good"),
    "DRUIDA": ("good", "poor", "good"),
    "FEITICEIRO": ("poor", "poor", "good"),
    "GUERREIRO": ("good", "poor", "poor"),
    "LADINO": ("poor", "good", "poor"),
    "MAGO": ("poor", "poor", "good"),
    "MONGE": ("good", "good", "good"),
    "PALADINO": ("good", "poor", "good"),
    "RANGER": ("good", "good", "poor"),
    "PATRULHEIRO": ("good", "good", "poor"),
}


def calcular_bonus_base_ataque(classe: str | None, nivel: int | None) -> str | None:
    classe_norm = normalizar_classe(classe or "")
    if not classe_norm:
        return None
    if nivel is None:
        return None
    nivel_val = max(1, min(20, int(nivel)))

    table_number = _TABLE_BY_CLASS.get(classe_norm)
    if table_number is not None:
        from_catalog = _buscar_bba_no_catalogo(table_number, nivel_val)
        if from_catalog:
            return from_catalog

    progression = _PROGRESSION_BY_CLASS.get(classe_norm)
    if not progression:
        return None
    return _calcular_bba_por_progressao(progression, nivel_val)


def calcular_resistencias_base(classe: str | None, nivel: int | None) -> tuple[int, int, int] | None:
    classe_norm = normalizar_classe(classe or "")
    if not classe_norm or nivel is None:
        return None
    nivel_val = max(1, min(20, int(nivel)))

    table_number = _TABLE_BY_CLASS.get(classe_norm)
    if table_number is not None:
        from_catalog = _buscar_resistencias_no_catalogo(table_number, nivel_val)
        if from_catalog is not None:
            return from_catalog

    progression = _SAVE_PROGRESSION_BY_CLASS.get(classe_norm)
    if not progression:
        return None
    fort_prog, reflex_prog, vontade_prog = progression
    return (
        _valor_resistencia_por_progressao(fort_prog, nivel_val),
        _valor_resistencia_por_progressao(reflex_prog, nivel_val),
        _valor_resistencia_por_progressao(vontade_prog, nivel_val),
    )


def _calcular_bba_por_progressao(progression: str, nivel: int) -> str:
    if progression == "good":
        total = nivel
    elif progression == "medium":
        total = (3 * nivel) // 4
    else:
        total = nivel // 2
    return _formatar_ataques_iterativos(total)


def _valor_resistencia_por_progressao(progression: str, nivel: int) -> int:
    if progression == "good":
        return 2 + (nivel // 2)
    return nivel // 3


def _formatar_ataques_iterativos(total: int) -> str:
    attacks: list[str] = []
    current = total
    while current >= 1:
        attacks.append(f"+{current}")
        current -= 5
    return "/".join(attacks) if attacks else "+0"


def _resolve_catalog_path() -> Path:
    path = Path(settings.CLASSES_TABLES_CATALOG_PATH)
    if path.is_absolute():
        return path
    candidate_backend = settings.BASE_DIR / path
    if candidate_backend.is_file():
        return candidate_backend
    return settings.BASE_DIR.parent / path


@lru_cache(maxsize=1)
def _load_catalog() -> dict:
    path = _resolve_catalog_path()
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _buscar_bba_no_catalogo(table_number: int, nivel: int) -> str | None:
    payload = _load_catalog()
    tables = payload.get("tables", [])
    if not isinstance(tables, list):
        return None
    target = next((t for t in tables if t.get("table_number") == table_number), None)
    if not isinstance(target, dict):
        return None
    rows = target.get("rows", [])
    if not isinstance(rows, list):
        return None

    for row in rows:
        if not isinstance(row, dict):
            continue
        values = [str(v).strip() for v in row.values() if str(v).strip()]
        if not values:
            continue
        level_idx = _index_nivel(values, nivel)
        if level_idx is None:
            continue
        candidate = _extrair_coluna_bba(values, level_idx)
        if candidate:
            return candidate
    return None


def _buscar_resistencias_no_catalogo(table_number: int, nivel: int) -> tuple[int, int, int] | None:
    payload = _load_catalog()
    tables = payload.get("tables", [])
    if not isinstance(tables, list):
        return None
    target = next((t for t in tables if t.get("table_number") == table_number), None)
    if not isinstance(target, dict):
        return None
    rows = target.get("rows", [])
    if not isinstance(rows, list):
        return None

    for row in rows:
        if not isinstance(row, dict):
            continue
        values = [str(v).strip() for v in row.values() if str(v).strip()]
        if not values:
            continue
        level_idx = _index_nivel(values, nivel)
        if level_idx is None:
            continue
        saves = _extrair_resistencias(values, level_idx)
        if saves is not None:
            return saves
    return None


def _index_nivel(values: list[str], nivel: int) -> int | None:
    for idx, value in enumerate(values):
        m = re.match(r"^(\d+)\s*[°ºo]?$", value)
        if m and int(m.group(1)) == nivel:
            return idx
    return None


def _extrair_coluna_bba(values: list[str], level_idx: int) -> str | None:
    pattern = re.compile(r"^[+]?\d+(?:/[+]?\d+)*$")
    for candidate in values[level_idx + 1 :]:
        if pattern.match(candidate):
            return _normalizar_bonus(candidate)
    return None


def _extrair_resistencias(values: list[str], level_idx: int) -> tuple[int, int, int] | None:
    # Após o nível vem BBA e depois as três TRs base (Fort/Ref/Vont).
    tokens = values[level_idx + 1 :]
    if not tokens:
        return None

    bba_idx = None
    pattern_bba = re.compile(r"^[+]?\d+(?:/[+]?\d+)*$")
    for idx, token in enumerate(tokens):
        if pattern_bba.match(token):
            bba_idx = idx
            break
    if bba_idx is None:
        return None

    numeric_tokens: list[int] = []
    for token in tokens[bba_idx + 1 :]:
        m = re.match(r"^[+]?(-?\d+)$", token)
        if m:
            numeric_tokens.append(int(m.group(1)))
        if len(numeric_tokens) == 3:
            break

    if len(numeric_tokens) < 3:
        return None
    return (numeric_tokens[0], numeric_tokens[1], numeric_tokens[2])


def _normalizar_bonus(raw: str) -> str:
    partes = [p.strip() for p in raw.split("/") if p.strip()]
    normalizadas: list[str] = []
    for parte in partes:
        if parte.startswith("+") or parte.startswith("-"):
            normalizadas.append(parte)
        else:
            normalizadas.append(f"+{parte}")
    return "/".join(normalizadas)
