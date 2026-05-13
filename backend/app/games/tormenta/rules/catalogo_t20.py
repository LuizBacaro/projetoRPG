"""Catálogos MB (equipamento, talentos) para autocomplete na ficha."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Tuple

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_EQUIP_JSON = _DATA_DIR / "equipamentos_mb_catalogo.json"


@lru_cache(maxsize=1)
def _carregar_equipamentos() -> List[Dict[str, Any]]:
    if not _EQUIP_JSON.is_file():
        return []
    raw = _EQUIP_JSON.read_text(encoding="utf-8")
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
        cat = str(row.get("categoria", "") or "").strip() or None

        def _s(key: str, mx: int) -> str | None:
            v = row.get(key)
            if v is None:
                return None
            t = str(v).strip()
            if not t:
                return None
            return t[:mx]

        out.append(
            {
                "nome": nome,
                "categoria": cat,
                "secao": _s("secao", 200),
                "custo": _s("custo", 80),
                "dano_p": _s("dano_p", 40),
                "dano_m": _s("dano_m", 40),
                "tipo_dano": _s("tipo_dano", 120),
                "critico": _s("critico", 80),
                "alcance": _s("alcance", 80),
                "peso": _s("peso", 80),
            }
        )
    return out


def lista_equipamentos_mb_catalogo() -> List[Dict[str, Any]]:
    """Lista completa de itens de equipamento (MB) para filtro/paginação."""
    return list(_carregar_equipamentos())


def filtrar_equipamentos_mb(
    q: str | None, skip: int, limit: int
) -> Tuple[List[Dict[str, Any]], int]:
    rows = [dict(r) for r in lista_equipamentos_mb_catalogo()]
    qn = (q or "").strip().lower()
    if qn:
        rows = [r for r in rows if qn in str(r.get("nome", "")).lower()]
    for i, item in enumerate(rows, start=1):
        item["id"] = i
    total = len(rows)
    s = max(0, int(skip))
    lim = max(1, min(200, int(limit)))
    return rows[s : s + lim], total


def _split_talentos_texto(texto: str) -> List[str]:
    """Separa nomes de talentos (vírgulas, ponto-e-vírgula, quebras de linha)."""
    if not texto or not str(texto).strip():
        return []
    partes = re.split(r"[,;\n]+", str(texto))
    return [p.strip() for p in partes if p and len(p.strip()) >= 2]


def lista_talentos_mb_catalogo() -> List[Dict[str, Any]]:
    """Talentos listados nas classes MB + deduplicação (nome canônico)."""
    from app.games.tormenta.rules.classes_t20 import lista_classes_mb

    seen: set[str] = set()
    out: List[Dict[str, Any]] = []
    for row in lista_classes_mb():
        raw = row.get("talentos_adicionais") or ""
        for nome in _split_talentos_texto(str(raw)):
            key = nome.lower()
            if key in seen:
                continue
            seen.add(key)
            out.append({"nome": nome})
    out.sort(key=lambda x: str(x["nome"]).lower())
    return out


def filtrar_talentos_mb(q: str | None, skip: int, limit: int) -> Tuple[List[Dict[str, Any]], int]:
    rows = [dict(r) for r in lista_talentos_mb_catalogo()]
    qn = (q or "").strip().lower()
    if qn:
        rows = [r for r in rows if qn in str(r.get("nome", "")).lower()]
    for i, item in enumerate(rows, start=1):
        item["id"] = i
    total = len(rows)
    s = max(0, int(skip))
    lim = max(1, min(200, int(limit)))
    return rows[s : s + lim], total
