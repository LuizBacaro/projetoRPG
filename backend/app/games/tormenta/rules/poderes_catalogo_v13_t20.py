"""Catálogo de poderes v1.3 — categorias p.124–136 e custo PM ao ativar."""

from __future__ import annotations

import re
import unicodedata
from functools import lru_cache
from typing import Any, Dict, List, Optional

CATEGORIAS_PODER_V13: List[str] = [
    "geral",
    "combate",
    "destino",
    "magia",
    "concedido",
    "tormenta",
    "classe",
]

_CATEGORIA_MAP = {
    "geral": "geral",
    "combate": "combate",
    "destino": "destino",
    "magia": "magia",
    "classe": "classe",
    "talento": "geral",
    "concedido": "concedido",
    "tormenta": "tormenta",
}

_PM_RE = re.compile(
    r"(?:gasta|gasto|custo|\+|\-|\()\s*(\d+)\s*pm\b",
    re.IGNORECASE,
)


def _norm_nome(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or ""))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def categoria_v13_de_item(
    row: Dict[str, Any],
    *,
    notas: str | None = None,
) -> str:
    """Normaliza categoria MB → slug v1.3 (p.124–136)."""
    nota_l = str(notas or row.get("notas") or "").lower()
    if "concedido" in nota_l or nota_l.startswith("auto:v13:concedido"):
        return "concedido"
    if "origem" in nota_l or nota_l.startswith("auto:v13:origem"):
        return "geral"
    if "versatil" in nota_l or nota_l.startswith("auto:v13:versatil"):
        return "geral"
    if row.get("categoria_v13"):
        cv = str(row["categoria_v13"]).strip().lower()
        if cv in _CATEGORIA_MAP.values():
            return cv
    cat = str(row.get("categoria") or "").strip().lower()
    if cat in _CATEGORIA_MAP:
        return _CATEGORIA_MAP[cat]
    sec = str(row.get("secao") or "").strip().lower()
    if "aprimoramento" in sec or "magia" in sec:
        return "magia"
    if "talentos das classes" in sec or cat == "classe":
        return "classe"
    return "geral"


def custo_pm_de_item(row: Dict[str, Any]) -> int:
    """Custo PM ao ativar (0 = passivo ou desconhecido)."""
    raw = row.get("custo_pm")
    if raw is not None:
        try:
            v = int(raw)
            return max(0, min(99, v))
        except (TypeError, ValueError):
            pass
    for key in ("descricao_resumo", "descricao", "prerequisitos"):
        txt = str(row.get(key) or "")
        m = _PM_RE.search(txt)
        if m:
            try:
                return max(0, min(99, int(m.group(1))))
            except (TypeError, ValueError):
                continue
    return 0


def enriquecer_item_catalogo_poder(row: Dict[str, Any]) -> Dict[str, Any]:
    from app.games.tormenta.rules.poderes_pre_requisitos_v13_t20 import (
        pre_requisitos_de_poder,
    )

    out = dict(row)
    out["categoria_v13"] = categoria_v13_de_item(out)
    out["custo_pm"] = custo_pm_de_item(out)
    reqs = pre_requisitos_de_poder(out)
    if reqs:
        out["pre_requisitos_v13"] = reqs
    return out


@lru_cache(maxsize=1)
def mapa_catalogo_poderes_por_nome() -> Dict[str, Dict[str, Any]]:
    from app.games.tormenta.rules.catalogo_t20 import lista_talentos_mb_catalogo

    out: Dict[str, Dict[str, Any]] = {}
    for row in lista_talentos_mb_catalogo():
        enriched = enriquecer_item_catalogo_poder(dict(row))
        nome = str(enriched.get("nome") or "").strip()
        if not nome:
            continue
        out[_norm_nome(nome)] = enriched
        out[nome.strip().lower()] = enriched
    return out


def metadados_poder_por_nome(
    nome: str,
    *,
    notas: str | None = None,
) -> Dict[str, Any]:
    """Resolve categoria_v13, custo_pm e pre_requisitos_v13 para um poder na ficha."""
    from app.games.tormenta.rules.poderes_pre_requisitos_v13_t20 import (
        pre_requisitos_de_poder,
    )

    n = str(nome or "").strip()
    if not n:
        return {"categoria_v13": "geral", "custo_pm": 0, "pre_requisitos_v13": []}
    m = mapa_catalogo_poderes_por_nome()
    row = m.get(_norm_nome(n)) or m.get(n.lower())
    if not row:
        row = {"nome": n, "categoria": "Geral"}
    cat = categoria_v13_de_item(row, notas=notas)
    pm = custo_pm_de_item(row)
    reqs = pre_requisitos_de_poder(row)
    return {
        "categoria_v13": cat,
        "custo_pm": pm,
        "pre_requisitos_v13": reqs,
    }
