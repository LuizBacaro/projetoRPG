"""Progressão de PV Tormenta 20 — tabelas fixas por classe + Constituição."""

from __future__ import annotations

from typing import Any, Dict, Optional

from app.games.tormenta.rules.atributos_t20 import contribuicao_atributo_t20
from app.games.tormenta.rules.classes_t20 import classe_por_slug, lista_classes
from app.games.tormenta.rules.conjuracao_t20 import pontos_magia_maximos_conjuracao
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)


def _mapa_classes_pv(regra_versao: Optional[str] = None) -> Dict[str, Dict[str, Any]]:
    return {str(c["slug"]).lower(): c for c in lista_classes(regra_versao)}


def classe_mb_por_slug(
    slug: str, regra_versao: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    return classe_por_slug(slug, regra_versao)


def pv_maximos_mb(
    slug_classe: str,
    nivel: int,
    con_valor: int,
    regra_versao: Optional[str] = None,
) -> Optional[int]:
    """
    PV máximos: pv_inicial + (nível−1)×pv_por_nível + nível×CON.

    Tabelas fixas (sem rolagem de dado por nível).
    """
    row = classe_por_slug(slug_classe, regra_versao)
    if not row:
        return None
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    nv = max(1, min(40, nv))
    pv_ini = int(row.get("pv_inicial", 8) or 8)
    pv_pn = int(row.get("pv_por_nivel", 2) or 0)
    mod_con = contribuicao_atributo_t20(int(con_valor), regra_versao)
    return pv_ini + max(0, nv - 1) * pv_pn + nv * mod_con


def preview_pv_mb(
    slug_classe: str,
    nivel: int,
    con_valor: int,
    regra_versao: Optional[str] = None,
    *,
    arcanista_caminho: Optional[str] = None,
    for_valor: int = 10,
    des_valor: int = 10,
    int_valor: int = 10,
    sab_valor: int = 10,
    car_valor: int = 10,
) -> Dict[str, Any]:
    """Breakdown PV/PM para API/UI."""
    rv = normalizar_regra_versao(regra_versao)
    row = classe_por_slug(slug_classe, rv)
    if not row:
        return {
            "classe_slug": slug_classe,
            "encontrado": False,
            "regra_versao": rv,
            "pv_max": None,
            "pm_max": None,
            "pm_por_nivel": None,
            "nivel": nivel,
            "mod_con": contribuicao_atributo_t20(int(con_valor), rv),
        }
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    nv = max(1, min(40, nv))
    mod_con = contribuicao_atributo_t20(int(con_valor), rv)
    pv_ini = int(row.get("pv_inicial", 8) or 8)
    pv_pn = int(row.get("pv_por_nivel", 2) or 0)
    de_niveis = max(0, nv - 1) * pv_pn
    de_con = nv * mod_con
    total = pv_ini + de_niveis + de_con
    pm_pn_raw = row.get("pm_por_nivel")
    pm_pn_i: Optional[int] = None
    if pm_pn_raw is not None:
        try:
            pm_pn_i = int(pm_pn_raw)
        except (TypeError, ValueError):
            pm_pn_i = None
    pm_max: Optional[int] = None
    if rv == REGRA_VERSAO_V13 and pm_pn_i is not None and pm_pn_i > 0:
        pm_max = nv * pm_pn_i
    elif rv != REGRA_VERSAO_V13:
        pm_max = pontos_magia_maximos_conjuracao(
            slug_classe,
            nv,
            for_valor,
            des_valor,
            con_valor,
            int_valor,
            sab_valor,
            car_valor,
            regra_versao=rv,
            arcanista_caminho=arcanista_caminho,
        )
    return {
        "classe_slug": str(slug_classe).strip().lower(),
        "classe_nome": str(row.get("nome", "")),
        "encontrado": True,
        "regra_versao": rv,
        "nivel": nv,
        "pv_inicial": pv_ini,
        "pv_por_nivel": pv_pn,
        "mod_con": mod_con,
        "contrib_niveis_extras": de_niveis,
        "contrib_constituicao": de_con,
        "pv_max": total,
        "pm_por_nivel": pm_pn_i,
        "pm_max": pm_max,
    }
