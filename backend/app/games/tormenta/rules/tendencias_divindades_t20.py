"""Listas MB — tendências (alinhamento) e divindades (panteão) para combos na ficha."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

_DATA = (
    Path(__file__).resolve().parent.parent / "data" / "tendencias_divindades_mb.json"
)


@lru_cache(maxsize=1)
def _documento() -> Dict[str, Any]:
    if not _DATA.is_file():
        return {"tendencias": [], "divindades": []}
    return json.loads(_DATA.read_text(encoding="utf-8"))


def _slug_fallback_de_rotulo(rotulo: str) -> str:
    base = rotulo.split(",")[0].strip().lower()
    base = re.sub(r"[^a-z0-9]+", "_", base)
    base = re.sub(r"_+", "_", base).strip("_")
    return (base or "divindade")[:40]


def lista_tendencias_mb() -> List[str]:
    rows = _documento().get("tendencias") or []
    out: List[str] = []
    if not isinstance(rows, list):
        return out
    for x in rows:
        if isinstance(x, str) and x.strip():
            out.append(x.strip())
    return out


def lista_divindades_mb() -> List[Dict[str, str]]:
    """Cada item: `slug` (chave estável) e `rotulo` (texto gravado no personagem)."""
    rows = _documento().get("divindades") or []
    out: List[Dict[str, str]] = []
    if not isinstance(rows, list):
        return out
    for x in rows:
        if isinstance(x, str) and x.strip():
            rot = x.strip()
            out.append({"slug": _slug_fallback_de_rotulo(rot), "rotulo": rot})
            continue
        if not isinstance(x, dict):
            continue
        rot = str(x.get("rotulo") or x.get("nome") or "").strip()
        if not rot:
            continue
        slug = str(x.get("slug") or "").strip().lower()
        if not slug:
            slug = _slug_fallback_de_rotulo(rot)
        slug = re.sub(r"[^a-z0-9_]", "", slug)[:40]
        out.append({"slug": slug or _slug_fallback_de_rotulo(rot), "rotulo": rot})
    return out
