"""Progressão de PV Tormenta 20 (MB) — tabelas fixas por classe + modificador de Constituição."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.games.tormenta.rules.atributos_t20 import modificador_atributo_t20
from app.games.tormenta.rules.classes_t20 import lista_classes_mb


def _mapa_classes_pv() -> Dict[str, Dict[str, Any]]:
    return {str(c["slug"]).lower(): c for c in lista_classes_mb()}


def classe_mb_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    s = str(slug or "").strip().lower()
    if not s:
        return None
    return _mapa_classes_pv().get(s)


def pv_maximos_mb(
    slug_classe: str,
    nivel: int,
    con_valor: int,
) -> Optional[int]:
    """
    PV máximos MB: pv_inicial + (nível−1)×pv_por_nível + nível×mod_CON.

    Tabelas fixas do Módulo Básico (sem rolagem de dado por nível).
    """
    row = classe_mb_por_slug(slug_classe)
    if not row:
        return None
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    nv = max(1, min(40, nv))
    pv_ini = int(row.get("pv_inicial", 8) or 8)
    pv_pn = int(row.get("pv_por_nivel", 2) or 0)
    mod_con = modificador_atributo_t20(int(con_valor))
    return pv_ini + max(0, nv - 1) * pv_pn + nv * mod_con


def preview_pv_mb(
    slug_classe: str,
    nivel: int,
    con_valor: int,
) -> Dict[str, Any]:
    """Breakdown para API/UI."""
    row = classe_mb_por_slug(slug_classe)
    if not row:
        return {
            "classe_slug": slug_classe,
            "encontrado": False,
            "pv_max": None,
            "nivel": nivel,
            "mod_con": modificador_atributo_t20(int(con_valor)),
        }
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    nv = max(1, min(40, nv))
    mod_con = modificador_atributo_t20(int(con_valor))
    pv_ini = int(row.get("pv_inicial", 8) or 8)
    pv_pn = int(row.get("pv_por_nivel", 2) or 0)
    de_niveis = max(0, nv - 1) * pv_pn
    de_con = nv * mod_con
    total = pv_ini + de_niveis + de_con
    return {
        "classe_slug": str(slug_classe).strip().lower(),
        "classe_nome": str(row.get("nome", "")),
        "encontrado": True,
        "nivel": nv,
        "pv_inicial": pv_ini,
        "pv_por_nivel": pv_pn,
        "mod_con": mod_con,
        "contrib_niveis_extras": de_niveis,
        "contrib_constituicao": de_con,
        "pv_max": total,
    }
