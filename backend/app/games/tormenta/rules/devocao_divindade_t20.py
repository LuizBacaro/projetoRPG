"""Prece de devoção por divindade MB — RF-T44d (truque sem PM para devotos)."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.tendencias_divindades_t20 import lista_divindades_mb

_DATA = Path(__file__).resolve().parent.parent / "data" / "devocao_divindade_mb.json"


@lru_cache(maxsize=1)
def _documento() -> Dict[str, Any]:
    if not _DATA.is_file():
        return {"divindades": {}}
    return json.loads(_DATA.read_text(encoding="utf-8"))


def _norm_slug(slug: str) -> str:
    return re.sub(r"[^a-z0-9_]", "", str(slug or "").strip().lower())[:40]


def truque_devocao_por_divindade_mb(divindade_slug: str) -> Optional[str]:
    """Slug da prece de devoção (círculo 0) concedida pela divindade, ou None."""
    s = _norm_slug(divindade_slug)
    if not s:
        return None
    divs = _documento().get("divindades") or {}
    row = divs.get(s) if isinstance(divs, dict) else None
    if not isinstance(row, dict):
        return None
    tr = str(row.get("truque_devocao_slug") or "").strip().lower()
    return tr or None


def magia_e_truque_devocao_mb(divindade_slug: str, magia_slug: str) -> bool:
    tr = truque_devocao_por_divindade_mb(divindade_slug)
    if not tr:
        return False
    return tr == str(magia_slug or "").strip().lower()


def lista_devocao_divindades_mb() -> List[Dict[str, Any]]:
    """Uma entrada por divindade com slug e truque_devocao_slug (para API identidade-mb)."""
    divs = _documento().get("divindades") or {}
    if not isinstance(divs, dict):
        return []
    out: List[Dict[str, Any]] = []
    for slug, row in sorted(divs.items()):
        if not isinstance(row, dict):
            continue
        tr = str(row.get("truque_devocao_slug") or "").strip().lower()
        if slug and tr:
            out.append({"divindade_slug": _norm_slug(slug), "truque_devocao_slug": tr})
    return out


def divindade_mb_slug_de_ficha(
    ficha_json: Optional[Dict[str, Any]],
    divindade_rotulo: Optional[str] = None,
) -> Optional[str]:
    """Resolve slug estável a partir de ficha_json ou rótulo gravado no personagem."""
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    salvo = str(fj.get("tormenta_divindade_mb_slug") or "").strip().lower()
    if salvo:
        return _norm_slug(salvo)
    rot = str(divindade_rotulo or fj.get("divindade") or "").strip()
    if not rot:
        return None
    rot_l = rot.lower()
    for d in lista_divindades_mb():
        if str(d.get("rotulo") or "").strip().lower() == rot_l:
            return _norm_slug(d.get("slug") or "")
        if rot_l in str(d.get("rotulo") or "").strip().lower():
            return _norm_slug(d.get("slug") or "")
    return None


def classe_usa_truque_devocao_mb(slug_classe: str) -> bool:
    return str(slug_classe or "").strip().lower() in (
        "clerigo",
        "druida",
        "paladino",
    )
