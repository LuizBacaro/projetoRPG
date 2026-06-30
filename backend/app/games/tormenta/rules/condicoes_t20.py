"""Condições Tormenta 20 v1.3 — catálogo p.394 e modificadores de combate (RF-T05-v13)."""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CATALOG_JSON = _DATA_DIR / "condicoes_v13_catalogo.json"

# Fallback legado MB (substring) — compatível com fichas/arena antigas.
_LEGACY_MOD_ATQ: Dict[str, int] = {
    "cego": -4,
    "atordoado": -4,
    "agarrado": -4,
    "enjoado": -2,
    "exausto": -2,
    "frustrado": -2,
    "lento": -2,
    "enredado": -2,
    "ofuscado": -2,
    "assustado": -2,
    "abalado": -2,
}

_LEGACY_MOD_CA: Dict[str, int] = {
    "surpreso": -4,
    "surpreendido": -5,
    "desprevenido": -5,
    "agarrado": -2,
    "atordoado": -2,
    "enjoado": -2,
    "frustrado": -2,
    "lento": -2,
    "vulneravel": -2,
    "vulnerável": -2,
    "indefeso": -10,
}


def _norm_chave(texto: Any) -> str:
    s = unicodedata.normalize("NFKD", str(texto or "").strip().lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return s.strip()


@lru_cache(maxsize=1)
def _carregar_catalogo_bruto() -> Dict[str, Any]:
    if not _CATALOG_JSON.is_file():
        return {"condicoes": [], "situacoes_especiais": []}
    return json.loads(_CATALOG_JSON.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _indice_por_chave() -> Dict[str, Dict[str, Any]]:
    idx: Dict[str, Dict[str, Any]] = {}
    data = _carregar_catalogo_bruto()
    for secao in ("condicoes", "situacoes_especiais"):
        for row in data.get(secao) or []:
            if not isinstance(row, dict):
                continue
            slug = str(row.get("slug") or "").strip().lower()
            nome = str(row.get("nome") or "").strip()
            if slug:
                idx[slug] = row
            if nome:
                idx[_norm_chave(nome)] = row
            for alias in row.get("aliases") or []:
                a = str(alias or "").strip()
                if a:
                    idx[_norm_chave(a)] = row
    return idx


def lista_condicoes_v13() -> List[Dict[str, Any]]:
    """Lista fechada Apêndice B (p.394)."""
    rows = _carregar_catalogo_bruto().get("condicoes") or []
    return [dict(r) for r in rows if isinstance(r, dict)]


def lista_situacoes_especiais_v13() -> List[Dict[str, Any]]:
    """Tabela 5-3 — situações de ataque/alvo."""
    rows = _carregar_catalogo_bruto().get("situacoes_especiais") or []
    return [dict(r) for r in rows if isinstance(r, dict)]


def resolver_entrada_condicao(rotulo: str) -> Optional[Dict[str, Any]]:
    """Resolve rótulo da arena (texto livre ou slug) para entrada do catálogo."""
    ch = _norm_chave(rotulo)
    if not ch:
        return None
    idx = _indice_por_chave()
    if ch in idx:
        return idx[ch]
    for key, row in idx.items():
        if key and key in ch:
            return row
    return None


def _acumular_mods_entrada(
    entry: Dict[str, Any],
    mods: Dict[str, int],
    visitados: Set[str],
) -> None:
    slug = str(entry.get("slug") or "").strip().lower()
    if slug and slug in visitados:
        return
    if slug:
        visitados.add(slug)
    try:
        mods["ataque"] += int(entry.get("mod_ataque") or 0)
    except (TypeError, ValueError):
        pass
    try:
        mods["ca"] += int(entry.get("mod_ca") or 0)
    except (TypeError, ValueError):
        pass
    for imp in entry.get("implica") or []:
        s = str(imp or "").strip().lower()
        if not s or s in visitados:
            continue
        implied = _indice_por_chave().get(s)
        if implied:
            _acumular_mods_entrada(implied, mods, visitados)


def modificadores_de_condicoes(
    rotulos: Optional[List[str]],
) -> Dict[str, int]:
    """
    Soma modificadores de ataque (atacante) e CA efetiva (alvo) a partir de rótulos.
    Compatível com catálogo v1.3 e rótulos legados MB.
    """
    mods = {"ataque": 0, "ca": 0}
    if not rotulos:
        return mods
    vistos_rotulo: Set[str] = set()
    slugs_aplicados: Set[str] = set()
    for raw in rotulos:
        ch = _norm_chave(raw)
        if not ch or ch in vistos_rotulo:
            continue
        vistos_rotulo.add(ch)
        entry = resolver_entrada_condicao(str(raw))
        if entry:
            _acumular_mods_entrada(entry, mods, slugs_aplicados)
        else:
            leg = _mods_legado(ch)
            mods["ataque"] += leg["ataque"]
            mods["ca"] += leg["ca"]
    return mods


def _mods_legado(chave: str) -> Dict[str, int]:
    mods = {"ataque": 0, "ca": 0}
    for key, val in _LEGACY_MOD_ATQ.items():
        if key in chave:
            mods["ataque"] += val
    for key, val in _LEGACY_MOD_CA.items():
        if key in chave:
            mods["ca"] += val
    return mods


def modificadores_de_condicoes_mb(
    rotulos: Optional[List[str]],
) -> Dict[str, int]:
    """Alias legado — preferir `modificadores_de_condicoes`."""
    return modificadores_de_condicoes(rotulos)
