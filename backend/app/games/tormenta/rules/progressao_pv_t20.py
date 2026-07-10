"""Progressão de PV Tormenta 20 — tabelas fixas por classe + Constituição."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

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


def _niveis_por_classe_de_lista(classes: List[Dict[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for item in classes or []:
        if not isinstance(item, dict):
            continue
        slug = str(item.get("slug") or "").strip().lower()
        if not slug:
            continue
        try:
            nv = int(item.get("nivel", 0))
        except (TypeError, ValueError):
            continue
        if nv < 1:
            continue
        out[slug] = out.get(slug, 0) + nv
    return out


def pm_bonus_meio_elfo(nivel: int) -> int:
    """Bônus cumulativo de PM do Meio-Elfo (Heróis de Arton).

    +1 PM a cada nível ímpar: nível 1 → +1, nível 3 → +2, nível 5 → +3, ...
    Fórmula: (nivel + 1) // 2
    """
    try:
        nv = max(0, int(nivel))
    except (TypeError, ValueError):
        nv = 0
    return (nv + 1) // 2


def pm_bonus_racial_ha_de_ficha(
    ficha_json: Optional[Dict[str, Any]], nivel: int
) -> int:
    """Bônus cumulativos de PM por traço racial HA (ex.: Meio-Elfo)."""
    from app.games.tormenta.rules.regra_versao_t20 import (
        SUPLEMENTO_HEROIS_ARTON,
        game_suplemento_de_ficha,
    )

    fj = ficha_json if isinstance(ficha_json, dict) else {}
    if game_suplemento_de_ficha(fj) != SUPLEMENTO_HEROIS_ARTON:
        return 0
    raw = str(fj.get("raca_tormenta_slug") or "").strip().lower()
    if raw == "meio_elfo":
        return pm_bonus_meio_elfo(nivel)
    if raw == "duende":
        du = fj.get("duende")
        if isinstance(du, dict) and du.get("geracao_aleatoria"):
            return 2
    return 0


def preview_pm_multiclasse_v13(
    classes: List[Dict[str, Any]],
    *,
    ficha_json: Optional[Dict[str, Any]] = None,
    nivel_personagem: Optional[int] = None,
) -> Dict[str, Any]:
    """Breakdown de PM máximos v1.3 para multiclasse (soma nível × pm/nível)."""
    niveis_map = _niveis_por_classe_de_lista(classes)
    breakdown: List[Dict[str, Any]] = []
    partes: List[str] = []
    total = 0
    for slug in sorted(niveis_map.keys()):
        nv = niveis_map[slug]
        row = classe_por_slug(slug, REGRA_VERSAO_V13)
        if not row:
            breakdown.append(
                {
                    "slug": slug,
                    "nome": slug,
                    "nivel": nv,
                    "pm_por_nivel": None,
                    "pm_classe": None,
                }
            )
            continue
        pm_pn_raw = row.get("pm_por_nivel")
        try:
            pm_pn = int(pm_pn_raw) if pm_pn_raw is not None else None
        except (TypeError, ValueError):
            pm_pn = None
        if pm_pn is None or pm_pn < 0:
            breakdown.append(
                {
                    "slug": slug,
                    "nome": str(row.get("nome", slug)),
                    "nivel": nv,
                    "pm_por_nivel": pm_pn,
                    "pm_classe": None,
                }
            )
            continue
        pm_classe = nv * pm_pn
        total += pm_classe
        nome = str(row.get("nome", slug))
        breakdown.append(
            {
                "slug": slug,
                "nome": nome,
                "nivel": nv,
                "pm_por_nivel": pm_pn,
                "pm_classe": pm_classe,
            }
        )
        partes.append(f"{nome} {nv}×{pm_pn}={pm_classe}")
    formula = " + ".join(partes) + (f" = {total} PM" if partes else "")
    bonus_racial = 0
    if ficha_json is not None:
        try:
            nv_bonus = (
                int(nivel_personagem)
                if nivel_personagem is not None
                else sum(niveis_map.values())
            )
        except (TypeError, ValueError):
            nv_bonus = sum(niveis_map.values()) if niveis_map else 1
        bonus_racial = pm_bonus_racial_ha_de_ficha(ficha_json, max(1, nv_bonus))
    if bonus_racial and total is not None:
        total += bonus_racial
        formula = (formula + f" + {bonus_racial} racial HA = {total} PM").strip()
    return {
        "regra_versao": REGRA_VERSAO_V13,
        "pm_max": total if partes or bonus_racial else None,
        "breakdown": breakdown,
        "formula": formula,
        "nivel_total_classes": sum(niveis_map.values()) if niveis_map else 0,
    }


def pm_maximos_v13_multiclasse(niveis_por_classe: Dict[str, int]) -> Optional[int]:
    """PM máximos v1.3 — soma nível × pm_por_nivel de cada classe (p.34)."""
    prev = preview_pm_multiclasse_v13(
        [{"slug": s, "nivel": n} for s, n in niveis_por_classe.items()]
    )
    return prev.get("pm_max")


def niveis_multiclasse_v13_de_ficha(
    ficha_json: Optional[Dict[str, Any]],
    nivel_personagem: int,
) -> List[Dict[str, Any]]:
    """Linhas ``[{slug, nivel}]`` — ``multiclasse_v13`` ou classe principal única."""
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    slug_pri = str(fj.get("tormenta_classe_mb_slug") or "").strip().lower()
    mc = fj.get("multiclasse_v13")
    if isinstance(mc, list) and mc:
        out: List[Dict[str, Any]] = []
        for item in mc:
            if not isinstance(item, dict):
                continue
            sl = str(item.get("slug") or "").strip().lower()
            if not sl:
                continue
            try:
                nv = int(item.get("nivel", 0))
            except (TypeError, ValueError):
                continue
            if nv < 1:
                continue
            out.append({"slug": sl, "nivel": min(40, nv)})
        if out:
            return out
    if slug_pri:
        try:
            nv = int(nivel_personagem)
        except (TypeError, ValueError):
            nv = 1
        return [{"slug": slug_pri, "nivel": max(1, min(40, nv))}]
    return []


def preview_pv_multiclasse_v13(
    classes: List[Dict[str, Any]],
    con_valor: int,
    slug_primario: str,
) -> Dict[str, Any]:
    """Breakdown PV máximos v1.3 multiclasse (p.34)."""
    niveis_map = _niveis_por_classe_de_lista(classes)
    mod_con = contribuicao_atributo_t20(int(con_valor), REGRA_VERSAO_V13)
    if not niveis_map:
        return {
            "regra_versao": REGRA_VERSAO_V13,
            "encontrado": False,
            "pv_max": None,
            "mod_con": mod_con,
            "contrib_constituicao": 0,
            "breakdown": [],
            "formula": "",
            "nivel_total_classes": 0,
            "slug_primario": str(slug_primario or "").strip().lower(),
        }
    pri = str(slug_primario or "").strip().lower()
    breakdown: List[Dict[str, Any]] = []
    partes: List[str] = []
    base = 0
    total_nv = 0
    todas_ok = True
    for slug in sorted(niveis_map.keys()):
        nv = niveis_map[slug]
        row = classe_por_slug(slug, REGRA_VERSAO_V13)
        primaria = slug == pri
        if not row:
            todas_ok = False
            breakdown.append(
                {
                    "slug": slug,
                    "nome": slug,
                    "nivel": nv,
                    "primaria": primaria,
                    "pv_inicial": None,
                    "pv_por_nivel": None,
                    "pv_classe": None,
                }
            )
            continue
        pv_ini = int(row.get("pv_inicial", 8) or 8)
        pv_pn = int(row.get("pv_por_nivel", 2) or 0)
        if primaria:
            pv_classe = pv_ini + max(0, nv - 1) * pv_pn
            partes.append(
                f"{row.get('nome', slug)} {pv_ini}+{max(0, nv - 1)}×{pv_pn}={pv_classe}"
            )
        else:
            pv_classe = nv * pv_pn
            partes.append(f"{row.get('nome', slug)} {nv}×{pv_pn}={pv_classe}")
        base += pv_classe
        total_nv += nv
        breakdown.append(
            {
                "slug": slug,
                "nome": str(row.get("nome", slug)),
                "nivel": nv,
                "primaria": primaria,
                "pv_inicial": pv_ini if primaria else None,
                "pv_por_nivel": pv_pn,
                "pv_classe": pv_classe,
            }
        )
    de_con = total_nv * mod_con
    pv_max = base + de_con if todas_ok and breakdown else None
    formula = ""
    if partes and pv_max is not None:
        con_txt = f"{total_nv}×{mod_con}" if mod_con != 0 else f"{total_nv}×CON"
        formula = " + ".join(partes) + f" + {con_txt} = {pv_max} PV"
    return {
        "regra_versao": REGRA_VERSAO_V13,
        "encontrado": pv_max is not None,
        "pv_max": pv_max,
        "mod_con": mod_con,
        "contrib_constituicao": de_con,
        "breakdown": breakdown,
        "formula": formula,
        "nivel_total_classes": total_nv,
        "slug_primario": pri,
    }


def pv_maximos_v13_multiclasse(
    classes: List[Dict[str, Any]],
    con_valor: int,
    slug_primario: str,
) -> Optional[int]:
    """PV máximos v1.3 multiclasse — soma por classe + CON × nível total (p.34)."""
    prev = preview_pv_multiclasse_v13(classes, con_valor, slug_primario)
    return prev.get("pv_max")
