"""Listas MB — tendências (alinhamento) e divindades (panteão) para combos na ficha."""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, FrozenSet, List

_DATA = (
    Path(__file__).resolve().parent.parent / "data" / "tendencias_divindades_mb.json"
)

_CLASSES_DEVOTO_OBRIGATORIO_V13: FrozenSet[str] = frozenset(
    {"clerigo", "druida", "paladino"}
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


def lista_divindades_mb() -> List[Dict[str, Any]]:
    """Cada item: `slug`, `rotulo` e metadados v1.3 opcionais."""
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
        item: Dict[str, Any] = {
            "slug": slug or _slug_fallback_de_rotulo(rot),
            "rotulo": rot,
        }
        if x.get("energia"):
            item["energia"] = str(x.get("energia"))
        pc = x.get("poderes_concedidos")
        if isinstance(pc, list):
            item["poderes_concedidos"] = [str(p) for p in pc if str(p).strip()]
        from app.games.tormenta.rules.divindades_obrigacoes_v13_t20 import (
            obrigacoes_divindade_v13,
        )

        obr = obrigacoes_divindade_v13(item["slug"])
        if obr.get("pagina") is not None:
            item["pagina"] = obr["pagina"]
        if obr.get("obrigacoes_flags"):
            item["obrigacoes_flags"] = obr["obrigacoes_flags"]
        if obr.get("sem_penalidade_obrigacao"):
            item["sem_penalidade_obrigacao"] = True
        out.append(item)
    return out


def divindade_por_slug(slug: str) -> Dict[str, Any] | None:
    s = str(slug or "").strip().lower()
    if not s:
        return None
    for row in lista_divindades_mb():
        if str(row.get("slug") or "").strip().lower() == s:
            return row
    return None


def divindade_por_rotulo(rotulo: str) -> Dict[str, Any] | None:
    r = str(rotulo or "").strip()
    if not r:
        return None
    for row in lista_divindades_mb():
        if str(row.get("rotulo") or "").strip() == r:
            return row
    return None


def classe_exige_devocao_v13(ficha_json: dict | None) -> bool:
    """Clérigo, druida e paladino são devotos automáticos (v1.3 p.96)."""
    fj = dict(ficha_json or {})
    slug = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
    return slug in _CLASSES_DEVOTO_OBRIGATORIO_V13


def validar_devocao_v13(
    ficha_json: dict | None,
    *,
    divindade_rotulo: str | None = None,
) -> tuple[bool, str]:
    """Valida devoto / poder concedido v1.3 (opcional; regras se preenchido)."""
    fj = dict(ficha_json or {})
    devoto = bool(fj.get("devoto")) or classe_exige_devocao_v13(fj)
    pcs = str(fj.get("poder_concedido_slug") or "").strip().lower()
    div_slug = str(fj.get("tormenta_divindade_mb_slug") or "").strip().lower()
    if not div_slug:
        row_rot = divindade_por_rotulo(divindade_rotulo or "")
        if row_rot:
            div_slug = str(row_rot.get("slug") or "").strip().lower()

    if devoto and not div_slug:
        if classe_exige_devocao_v13(fj):
            return False, "Clérigo, druida e paladino devem escolher uma divindade."
        return False, "Devoto: escolha uma divindade (Os Vinte)."
    if devoto and not pcs:
        if classe_exige_devocao_v13(fj):
            return (
                False,
                "Clérigo, druida e paladino devem escolher um poder concedido.",
            )
        return False, "Devoto: escolha um poder concedido da divindade."
    if pcs and not div_slug:
        return False, "Poder concedido exige divindade escolhida."
    if pcs and div_slug:
        row = divindade_por_slug(div_slug)
        if not row:
            return False, "Divindade desconhecida."
        pool = {
            str(p).strip().lower()
            for p in (row.get("poderes_concedidos") or [])
            if str(p).strip()
        }
        if pcs not in pool:
            return False, "Poder concedido invalido para a divindade escolhida."
    return True, ""
