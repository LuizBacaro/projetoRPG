"""Catálogo de armaduras / itens de proteção (Tormenta 20) — preenchível a partir do livro."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_ARM_JSON = _DATA_DIR / "armaduras_protecao_catalogo.json"


@lru_cache(maxsize=1)
def _carregar_armaduras() -> List[Dict[str, Any]]:
    if not _ARM_JSON.is_file():
        return []
    raw = _ARM_JSON.read_text(encoding="utf-8")
    data = json.loads(raw)
    rows = data.get("itens") or data.get("items") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        nome = str(row.get("nome", "")).strip()
        if not nome:
            continue
        out.append(
            {
                "nome": nome,
                "tipo": str(row.get("tipo", "") or "").strip() or "",
                "bonus_ca": int(row.get("bonus_ca", 0) or 0),
                "penalidade": int(row.get("penalidade", 0) or 0),
                "des_max": str(row.get("des_max", "") or "").strip() or None,
                "falha_arcana": str(row.get("falha_arcana", "") or "").strip() or None,
                "deslocamento": str(row.get("deslocamento", "") or "").strip() or None,
                "peso": str(row.get("peso", "") or "").strip() or None,
                "propriedades_especiais": str(
                    row.get("propriedades_especiais", "") or ""
                ).strip()
                or None,
            }
        )
    return out


def lista_armaduras_protecao_catalogo() -> List[Dict[str, Any]]:
    return list(_carregar_armaduras())


def filtrar_armaduras_protecao_mb(
    q: str | None, skip: int, limit: int
) -> Tuple[List[Dict[str, Any]], int]:
    rows = [dict(r) for r in lista_armaduras_protecao_catalogo()]
    qn = (q or "").strip().lower()
    if qn:
        rows = [
            r
            for r in rows
            if qn in str(r.get("nome", "")).lower()
            or qn in str(r.get("tipo", "")).lower()
        ]
    for i, item in enumerate(rows, start=1):
        item["id"] = i
    total = len(rows)
    s = max(0, int(skip))
    lim = max(1, min(200, int(limit)))
    return rows[s : s + lim], total
