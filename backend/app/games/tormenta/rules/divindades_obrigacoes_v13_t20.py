"""Obrigações e restrições de devoção v1.3 (RF-T09h, Tabela 1-20 p.96–105)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List

_DATA = (
    Path(__file__).resolve().parent.parent / "data" / "divindades_obrigacoes_v13.json"
)


@lru_cache(maxsize=1)
def _documento() -> Dict[str, Any]:
    if not _DATA.is_file():
        return {"por_slug": {}}
    return json.loads(_DATA.read_text(encoding="utf-8"))


def obrigacoes_divindade_v13(slug: str) -> Dict[str, Any]:
    """Metadados de O&R para uma divindade (Os Vinte)."""
    s = str(slug or "").strip().lower()
    raw = (_documento().get("por_slug") or {}).get(s) or {}
    flags = raw.get("obrigacoes_flags") or []
    out_flags: List[Dict[str, str]] = []
    if isinstance(flags, list):
        for row in flags:
            if not isinstance(row, dict):
                continue
            fslug = str(row.get("slug") or "").strip()
            rot = str(row.get("rotulo") or "").strip()
            if fslug and rot:
                out_flags.append({"slug": fslug, "rotulo": rot})
    pagina = raw.get("pagina")
    try:
        pag = int(pagina) if pagina is not None else None
    except (TypeError, ValueError):
        pag = None
    return {
        "pagina": pag,
        "obrigacoes_flags": out_flags,
        "sem_penalidade_obrigacao": bool(raw.get("sem_penalidade_obrigacao")),
    }
