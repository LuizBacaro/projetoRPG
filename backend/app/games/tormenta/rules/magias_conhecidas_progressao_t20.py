"""Progressão de magias conhecidas MB — bardo e feiticeiro (RF-T42)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from app.games.tormenta.rules.grimorio_conjuracao_t20 import (
    modo_conjuracao_classe,
    slug_efetivo_tabelas_magia_mb,
)
from app.games.tormenta.rules.magias_progressao_mb_t20 import (
    circulo_maximo_magias_lancaveis_mb,
)

_DATA = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "magias_conhecidas_progressao_mb.json"
)


@lru_cache(maxsize=1)
def _carregar() -> Dict[str, Any]:
    if not _DATA.is_file():
        return {"classes": {}}
    return json.loads(_DATA.read_text(encoding="utf-8"))


def _classe_row(slug_classe: str) -> Optional[Dict[str, Any]]:
    s = str(slug_classe or "").strip().lower()
    if not s:
        return None
    classes = _carregar().get("classes") or {}
    row = classes.get(s)
    return row if isinstance(row, dict) else None


def classe_usa_limite_conhecidas_mb(
    slug_classe: str,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> bool:
    """Espontâneo ou bruxo (foco) com tabela de conhecidas."""
    modo = modo_conjuracao_classe(slug_classe, regra_versao, arcanista_caminho)
    if modo not in ("espontaneo", "foco"):
        return False
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    return _classe_row(eff) is not None


def tabela_conhecidas_por_nivel_mb(
    slug_classe: str,
    nivel: int,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Optional[List[int]]:
    """Lista por círculo (índice = círculo): máximo de magias conhecidas naquele círculo."""
    eff = slug_efetivo_tabelas_magia_mb(slug_classe, regra_versao, arcanista_caminho)
    row = _classe_row(eff)
    if not row:
        return None
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    nv = max(1, min(20, nv))
    por = row.get("por_nivel") or {}
    vals = por.get(str(nv))
    if not isinstance(vals, list):
        vals = por.get(str(1))
    if not isinstance(vals, list):
        return None
    return [max(0, int(x)) for x in vals]


def limite_magias_conhecidas_circulo_mb(
    slug_classe: str,
    nivel: int,
    circulo: int,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Optional[int]:
    tab = tabela_conhecidas_por_nivel_mb(
        slug_classe,
        nivel,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    if tab is None:
        return None
    try:
        c = int(circulo)
    except (TypeError, ValueError):
        c = 0
    if c < 0 or c >= len(tab):
        return 0
    return int(tab[c])


def total_magias_conhecidas_max_mb(
    slug_classe: str,
    nivel: int,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Optional[int]:
    tab = tabela_conhecidas_por_nivel_mb(
        slug_classe,
        nivel,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    if tab is None:
        return None
    return int(sum(tab))


def niveis_troca_magia_bardo_mb() -> List[int]:
    row = _classe_row("bardo")
    if not row:
        return []
    raw = row.get("troca_nos_niveis") or []
    out: List[int] = []
    for x in raw:
        try:
            out.append(int(x))
        except (TypeError, ValueError):
            continue
    return sorted(set(out))


def bardo_pode_trocar_magia_mb(nivel: int) -> bool:
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    return nv in niveis_troca_magia_bardo_mb()


def contar_conhecidas_por_circulo(
    vinculos: List[Dict[str, Any]],
    *,
    metadados_por_slug: Optional[Dict[str, Dict[str, Any]]] = None,
) -> Dict[int, int]:
    """Conta vínculos com papel conhecida agrupados por círculo do catálogo."""
    meta_map = metadados_por_slug or {}
    out: Dict[int, int] = {}
    for v in vinculos:
        if not isinstance(v, dict):
            continue
        if str(v.get("papel", "")).strip().lower() != "conhecida":
            continue
        slug = str(v.get("magia_slug") or "").strip().lower()
        circ = None
        if v.get("circulo") is not None:
            try:
                circ = int(v["circulo"])
            except (TypeError, ValueError):
                circ = None
        if circ is None and slug in meta_map:
            try:
                circ = int(meta_map[slug].get("circulo", 0) or 0)
            except (TypeError, ValueError):
                circ = 0
        if circ is None:
            circ = 0
        out[circ] = out.get(circ, 0) + 1
    return out


def validar_adicionar_conhecida_mb(
    *,
    slug_classe: str,
    nivel: int,
    circulo_magia: int,
    vinculos_existentes: List[Dict[str, Any]],
    metadados_por_slug: Optional[Dict[str, Dict[str, Any]]] = None,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Tuple[bool, str]:
    if not classe_usa_limite_conhecidas_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    ):
        return True, ""
    try:
        circ = int(circulo_magia)
    except (TypeError, ValueError):
        circ = 0
    cmax = circulo_maximo_magias_lancaveis_mb(
        slug_classe,
        nivel,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    if circ > cmax:
        return (
            False,
            f"Magia de {circ}º círculo: esta classe no nível {nivel} só lança até o {cmax}º círculo (MB).",
        )
    lim = limite_magias_conhecidas_circulo_mb(
        slug_classe,
        nivel,
        circ,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    if lim is None:
        return True, ""
    counts = contar_conhecidas_por_circulo(
        vinculos_existentes, metadados_por_slug=metadados_por_slug
    )
    usado = counts.get(circ, 0)
    if usado >= lim:
        return (
            False,
            f"Limite de magias conhecidas no {circ}º círculo: {usado}/{lim} (MB, {slug_classe}).",
        )
    return True, ""


def preview_magias_conhecidas_mb(
    *,
    slug_classe: str,
    nivel: int,
    vinculos: Optional[List[Dict[str, Any]]] = None,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> Dict[str, Any]:
    from app.games.tormenta.rules.catalogo_t20 import metadados_magia_mb_por_slug

    vinculos = vinculos or []
    tab = tabela_conhecidas_por_nivel_mb(
        slug_classe,
        nivel,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    usa = classe_usa_limite_conhecidas_mb(
        slug_classe,
        regra_versao=regra_versao,
        arcanista_caminho=arcanista_caminho,
    )
    meta: Dict[str, Dict[str, Any]] = {}
    for v in vinculos:
        if not isinstance(v, dict):
            continue
        sl = str(v.get("magia_slug") or "").strip().lower()
        if sl and sl not in meta:
            m = metadados_magia_mb_por_slug(sl)
            if m:
                meta[sl] = m
    counts = contar_conhecidas_por_circulo(vinculos, metadados_por_slug=meta)
    total_usado = sum(counts.values())
    total_max = (
        total_magias_conhecidas_max_mb(
            slug_classe,
            nivel,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        )
        if usa
        else None
    )
    por_circulo = []
    if tab:
        for c, lim in enumerate(tab):
            if lim <= 0 and counts.get(c, 0) <= 0:
                continue
            por_circulo.append(
                {
                    "circulo": c,
                    "limite": lim,
                    "usadas": counts.get(c, 0),
                }
            )
    return {
        "classe_slug": str(slug_classe).strip().lower(),
        "nivel": int(nivel),
        "usa_limite_conhecidas": usa,
        "total_conhecidas_usadas": total_usado,
        "total_conhecidas_max": total_max,
        "por_circulo": por_circulo,
        "circulo_max_lancavel": circulo_maximo_magias_lancaveis_mb(
            slug_classe,
            nivel,
            regra_versao=regra_versao,
            arcanista_caminho=arcanista_caminho,
        ),
        "bardo_pode_trocar": (
            bardo_pode_trocar_magia_mb(nivel)
            if str(slug_classe).strip().lower() == "bardo"
            else False
        ),
        "niveis_troca_bardo": niveis_troca_magia_bardo_mb(),
    }
