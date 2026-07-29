"""Catálogo do Livro dos Monstros D&D 3.5 — listagem e lookup."""

from __future__ import annotations

import json
import math
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

_DATA = Path(__file__).resolve().parent.parent / "data" / "bestiario_mm35.json"
_SLUG_RE = re.compile(r"[^a-z0-9]+")


def _norm(s: str) -> str:
    return _SLUG_RE.sub("-", str(s or "").strip().lower()).strip("-")


def _nd_numerico(raw: Any) -> Optional[float]:
    if raw is None or raw == "":
        return None
    if isinstance(raw, (int, float)):
        return float(raw)
    text = str(raw).strip().replace(",", ".")
    if "/" in text:
        a, b = text.split("/", 1)
        try:
            return float(a) / float(b)
        except (TypeError, ValueError, ZeroDivisionError):
            return None
    try:
        return float(text)
    except (TypeError, ValueError):
        return None


@lru_cache(maxsize=1)
def _carregar() -> List[Dict[str, Any]]:
    if not _DATA.is_file():
        return []
    data = json.loads(_DATA.read_text(encoding="utf-8"))
    rows = data.get("criaturas") or []
    out: List[Dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = _norm(str(row.get("slug") or ""))
        if not slug:
            continue
        item = dict(row)
        item["slug"] = slug
        item["fonte"] = str(item.get("fonte") or "mm35")
        out.append(item)
    return out


def limpar_cache_bestiario() -> None:
    _carregar.cache_clear()


def lista_bestiario_mm35() -> List[Dict[str, Any]]:
    return list(_carregar())


def obter_bestiario_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    alvo = _norm(slug)
    if not alvo:
        return None
    for row in _carregar():
        if row.get("slug") == alvo:
            return dict(row)
        aliases = row.get("aliases") or []
        if isinstance(aliases, list) and any(_norm(a) == alvo for a in aliases):
            return dict(row)
    return None


def filtrar_bestiario_mm35(
    *,
    q: Optional[str] = None,
    tipo: Optional[str] = None,
    nd_min: Optional[float] = None,
    nd_max: Optional[float] = None,
    skip: int = 0,
    limit: int = 50,
) -> Tuple[List[Dict[str, Any]], int]:
    termo = _norm(q or "").replace("-", " ")
    tipo_n = _norm(tipo or "")
    rows: List[Dict[str, Any]] = []
    for row in _carregar():
        if tipo_n:
            tipo_row = _norm(str(row.get("tipo_criatura") or ""))
            if tipo_n not in tipo_row and tipo_n != tipo_row:
                continue
        nd = _nd_numerico(row.get("nd"))
        if nd_min is not None and (nd is None or nd < nd_min):
            continue
        if nd_max is not None and (nd is None or nd > nd_max):
            continue
        if termo:
            blob = " ".join(
                [
                    str(row.get("nome") or ""),
                    str(row.get("slug") or ""),
                    str(row.get("tipo_criatura") or ""),
                    " ".join(str(a) for a in (row.get("aliases") or [])),
                ]
            ).lower()
            if termo not in _norm(blob).replace("-", " ") and termo not in blob:
                continue
        rows.append(row)
    total = len(rows)
    skip = max(0, int(skip or 0))
    limit = max(1, min(200, int(limit or 50)))
    return rows[skip : skip + limit], total


def resumo_bestiario(row: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "slug": row.get("slug"),
        "nome": row.get("nome"),
        "nd": row.get("nd"),
        "nd_rotulo": row.get("nd_rotulo"),
        "tipo_criatura": row.get("tipo_criatura"),
        "tamanho": row.get("tamanho"),
        "hp_maximo": row.get("hp_maximo"),
        "ca": row.get("ca"),
        "toque": row.get("toque"),
        "surpresa": row.get("surpresa"),
        "pagina_referencia": row.get("pagina_referencia"),
        "fonte": row.get("fonte"),
        "especie_pai": row.get("especie_pai"),
        "categoria_idade": row.get("categoria_idade"),
        "descricao_curta": row.get("descricao_curta") or "",
    }


def nivel_sugerido(row: Dict[str, Any]) -> int:
    nd = _nd_numerico(row.get("nd"))
    if nd is not None:
        return max(1, min(20, int(math.ceil(nd))))
    dv = str(row.get("dv") or "")
    m = re.match(r"(\d+)d", dv)
    if m:
        return max(1, min(20, int(m.group(1))))
    return 1


__all__ = [
    "filtrar_bestiario_mm35",
    "limpar_cache_bestiario",
    "lista_bestiario_mm35",
    "nivel_sugerido",
    "obter_bestiario_por_slug",
    "resumo_bestiario",
]
