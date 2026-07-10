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


_MOD_CAMPOS = (
    "ataque",
    "ca",
    "pericia",
    "pericia_fisica",
    "percepcao",
    "reflexos",
    "iniciativa",
    "atributo_fisico",
    "atributo_mental",
)

_ATRIBUTO_FISICO = frozenset({"for", "des", "con"})
_ATRIBUTO_MENTAL = frozenset({"int", "sab", "car"})


def _mods_vazios() -> Dict[str, int]:
    return {k: 0 for k in _MOD_CAMPOS}


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
    for campo in _MOD_CAMPOS:
        chave_json = (
            f"mod_{campo}"
            if campo != "ataque" and campo != "ca"
            else ("mod_ataque" if campo == "ataque" else "mod_ca")
        )
        try:
            mods[campo] += int(entry.get(chave_json) or 0)
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
    mods = _mods_vazios()
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


def modificador_condicao_pericia(
    slug_ou_nome: str,
    rotulos: Optional[List[str]],
    *,
    regra_versao: str = "v13",
) -> int:
    """Soma modificadores de condição aplicáveis a uma perícia (p.394 v1.3)."""
    from app.games.tormenta.rules.pericias_t20 import meta_pericia_por_nome

    mods = modificadores_de_condicoes(rotulos)
    total = int(mods.get("pericia", 0))
    meta = meta_pericia_por_nome(slug_ou_nome, regra_versao) or {}
    slug = str(meta.get("slug") or slug_ou_nome or "").strip().lower()
    atr = str(meta.get("atributo") or "").strip().lower()
    if int(mods.get("pericia_fisica", 0)) and atr in _ATRIBUTO_FISICO:
        total += int(mods["pericia_fisica"])
    if slug == "percepcao":
        total += int(mods.get("percepcao", 0))
    if slug == "reflexos":
        total += int(mods.get("reflexos", 0))
    if atr in _ATRIBUTO_FISICO:
        total += int(mods.get("atributo_fisico", 0))
    if atr in _ATRIBUTO_MENTAL:
        total += int(mods.get("atributo_mental", 0))
    return total


def _mods_legado(chave: str) -> Dict[str, int]:
    mods = _mods_vazios()
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
