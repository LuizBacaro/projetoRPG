"""
Cálculo de Bônus Base de Ataque (BBA) para classes D&D 3.5.

Canónico: `app.games.dnd35.bonus_base_ataque`.

Fonte primária: catálogo consolidado em `docs/dados/tabelas_classes_catalogo.json`.
Fallback: progressões padrão (boa/média/ruim) para manter robustez caso o catálogo
não esteja disponível no ambiente.
"""

from __future__ import annotations

from functools import lru_cache
import json
from pathlib import Path
import re

from app.shared.core.config import settings

from app.games.dnd35.text_utils import normalizar_classe

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
    classe_norm = _resolver_chave_classe(classe or "")
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
    classe_norm = _resolver_chave_classe(classe or "")
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
    """
    Após o marcador de nível: BBA, Fortitude, Reflexos, Vontade (e depois texto da coluna Especial).

    Preferência: leitura posicional (evita confundir dois '+0' quando o primeiro é BBA e o segundo é Fort).
    Fallback: heurística antiga (primeiro token com formato de BBA).
    """
    tokens = values[level_idx + 1 :]
    if not tokens:
        return None

    if len(tokens) >= 4:
        fort_ref_vont: list[int] = []
        ok = True
        for i in range(1, 4):
            m = re.match(r"^[+]?(-?\d+)$", tokens[i])
            if not m:
                ok = False
                break
            fort_ref_vont.append(int(m.group(1)))
        if ok:
            return (fort_ref_vont[0], fort_ref_vont[1], fort_ref_vont[2])

    # Fallback: localizar coluna de BBA e as três TRs subsequentes
    pattern_bba = re.compile(r"^[+]?\d+(?:/[+]?\d+)*$")
    bba_idx = None
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


def _resolver_chave_classe(classe: str) -> str:
    """
    Resolve chave de classe canônica mesmo quando o texto vem com ruído
    (ex.: sufixos, observações ou formatos legados).
    """
    base = normalizar_classe(classe or "")
    if base in _TABLE_BY_CLASS or base in _PROGRESSION_BY_CLASS:
        return base

    # Fallback por contenção: escolhe a maior chave encontrada no texto.
    # Ex.: "GUERREIRO (HUMANO)" -> "GUERREIRO"
    candidates = [
        key for key in _TABLE_BY_CLASS.keys()
        if key and key in base
    ]
    if not candidates:
        return base
    return max(candidates, key=len)


def calcular_habilidades_especiais_por_nivel(classe: str | None, nivel: int | None) -> list[dict]:
    classe_norm = _resolver_chave_classe(classe or "")
    if not classe_norm or nivel is None:
        return []
    nivel_val = max(1, min(20, int(nivel)))
    table_number = _TABLE_BY_CLASS.get(classe_norm)
    if table_number is None:
        return []

    payload = _load_catalog()
    tables = payload.get("tables", [])
    if not isinstance(tables, list):
        return []
    target = next((t for t in tables if t.get("table_number") == table_number), None)
    if not isinstance(target, dict):
        return []
    rows = target.get("rows", [])
    if not isinstance(rows, list):
        return []

    por_nivel: list[dict] = []

    for row in rows:
        if not isinstance(row, dict):
            continue
        values = [str(v).strip() for v in row.values() if str(v).strip()]
        if not values:
            continue
        encontrado = _encontrar_indice_e_nivel_linha(values)
        if encontrado is None:
            continue
        idx, nivel_row = encontrado
        if nivel_row < 1 or nivel_row > nivel_val:
            continue
        especial = _extrair_especial(values, idx)
        if not especial:
            continue
        habilidades_nivel: list[str] = []
        vistos_no_nivel: set[str] = set()
        for item in re.split(r"[,;]", especial):
            talento = item.strip()
            if not talento or talento in {"-", "—"}:
                continue
            key = talento.lower()
            if key in vistos_no_nivel:
                continue
            vistos_no_nivel.add(key)
            habilidades_nivel.append(talento)
        if habilidades_nivel:
            por_nivel.append({"nivel": nivel_row, "habilidades": habilidades_nivel})
    por_nivel.sort(key=lambda item: item["nivel"])
    return por_nivel


def calcular_habilidades_especiais(classe: str | None, nivel: int | None) -> list[str]:
    """Lista única (ordem de aparição) para fallback legado `a | b`; use `*_por_nivel` para o detalhe por nível."""
    grouped = calcular_habilidades_especiais_por_nivel(classe, nivel)
    flat: list[str] = []
    vistos: set[str] = set()
    for item in grouped:
        for habilidade in item.get("habilidades", []):
            h = str(habilidade)
            key = h.lower()
            if key in vistos:
                continue
            vistos.add(key)
            flat.append(h)
    return flat


def _extrair_especial(values: list[str], level_idx: int) -> str | None:
    after = values[level_idx + 1 :]
    if not after:
        return None

    # Prioriza token com texto descritivo (não numérico), que normalmente é a coluna Especial.
    candidates = []
    for token in after:
        if token in {"-", "—"}:
            continue
        if re.match(r"^[+]?\d+(?:/[+]?\d+)*$", token):
            continue
        if re.match(r"^[+]?\d+$", token):
            continue
        if re.search(r"[A-Za-zÀ-ÿ]", token):
            candidates.append(token)
    if not candidates:
        return None
    return candidates[0]


def _parse_nivel(value: str) -> int | None:
    m = re.match(r"^(\d+)\s*[°ºo]?$", str(value).strip())
    if not m:
        return None
    return int(m.group(1))


def _encontrar_indice_e_nivel_linha(values: list[str]) -> tuple[int, int] | None:
    """Localiza a primeira célula que indica o nível da linha (ex.: `6°`)."""
    for idx, raw in enumerate(values):
        nivel = _parse_nivel(raw)
        if nivel is not None:
            return (idx, nivel)
    return None


def _normalizar_bonus(raw: str) -> str:
    partes = [p.strip() for p in raw.split("/") if p.strip()]
    normalizadas: list[str] = []
    for parte in partes:
        if parte.startswith("+") or parte.startswith("-"):
            normalizadas.append(parte)
        else:
            normalizadas.append(f"+{parte}")
    return "/".join(normalizadas)
