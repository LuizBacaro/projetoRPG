"""Catálogo v1.3 — itens superiores (Tabelas 3-7/3-8) e materiais especiais (3-9)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA = Path(__file__).resolve().parent.parent / "data" / "itens_superiores_v13.json"


@lru_cache(maxsize=1)
def _documento() -> Dict[str, Any]:
    if not _DATA.is_file():
        return {
            "precos_melhoria": [300, 3000, 9000, 18000],
            "melhorias": [],
            "materiais": [],
        }
    raw = json.loads(_DATA.read_text(encoding="utf-8"))
    return raw if isinstance(raw, dict) else {}


def precos_melhoria_v13() -> List[int]:
    rows = _documento().get("precos_melhoria") or [300, 3000, 9000, 18000]
    out: List[int] = []
    for v in rows:
        try:
            out.append(int(v))
        except (TypeError, ValueError):
            continue
    return out or [300, 3000, 9000, 18000]


def lista_melhorias_v13(*, aplica_em: Optional[str] = None) -> List[Dict[str, Any]]:
    filtro = str(aplica_em or "").strip().lower() or None
    out: List[Dict[str, Any]] = []
    for row in _documento().get("melhorias") or []:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug") or "").strip().lower()
        nome = str(row.get("nome") or "").strip()
        if not slug or not nome:
            continue
        aplica = [
            str(x).strip().lower()
            for x in (row.get("aplica_em") or [])
            if str(x).strip()
        ]
        if filtro and filtro not in aplica:
            continue
        item = dict(row)
        item["slug"] = slug
        item["nome"] = nome
        item["aplica_em"] = aplica
        out.append(item)
    return out


def lista_materiais_especiais_v13(
    *, aplica_em: Optional[str] = None
) -> List[Dict[str, Any]]:
    filtro = str(aplica_em or "").strip().lower() or None
    out: List[Dict[str, Any]] = []
    for row in _documento().get("materiais") or []:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug") or "").strip().lower()
        nome = str(row.get("nome") or "").strip()
        if not slug or not nome:
            continue
        aplica = [
            str(x).strip().lower()
            for x in (row.get("aplica_em") or [])
            if str(x).strip()
        ]
        if filtro and filtro not in aplica:
            continue
        item = dict(row)
        item["slug"] = slug
        item["nome"] = nome
        item["aplica_em"] = aplica
        out.append(item)
    return out


def resumo_itens_superiores_v13(*, aplica_em: Optional[str] = None) -> Dict[str, Any]:
    return {
        "precos_melhoria": precos_melhoria_v13(),
        "precos_melhoria_detalhe": list(
            _documento().get("precos_melhoria_detalhe") or []
        ),
        "melhorias": lista_melhorias_v13(aplica_em=aplica_em),
        "materiais": lista_materiais_especiais_v13(aplica_em=aplica_em),
        "max_melhorias": 4,
    }


def custo_melhorias_ts(n_melhorias: int) -> int:
    """Soma cumulativa Tabela 3-7 para n melhorias (1–4)."""
    precos = precos_melhoria_v13()
    n = max(0, min(4, int(n_melhorias or 0)))
    return sum(precos[:n])


def parse_custo_ts(texto: Optional[str]) -> int:
    """Extrai inteiro de strings como 'T$ 15' / '15 T$' / '—'."""
    import re

    s = str(texto or "").strip()
    if not s or s in ("—", "-", "–"):
        return 0
    m = re.search(r"(\d[\d.]*)", s.replace(".", "").replace(",", ""))
    if not m:
        m2 = re.search(r"(\d+)", s)
        return int(m2.group(1)) if m2 else 0
    try:
        return int(float(m.group(1)))
    except ValueError:
        return 0
