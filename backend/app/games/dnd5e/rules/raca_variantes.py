"""Escolhas de variantes raciais (draconato, tiefling) — resistência e preview."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.dnd5e.data.raca_variantes_catalogo import RACA_VARIANTES

CATEGORIAS_DANO_RESISTENCIA = frozenset(
    {
        "acido",
        "acid",
        "eletricidade",
        "lightning",
        "fogo",
        "fire",
        "frio",
        "cold",
        "veneno",
        "poison",
    }
)


def raca_exige_variante(raca_slug: str) -> bool:
    return (raca_slug or "").strip().lower() in RACA_VARIANTES


def listar_variantes_raca(raca_slug: str) -> List[Dict[str, Any]]:
    key = (raca_slug or "").strip().lower()
    return [dict(v) for v in RACA_VARIANTES.get(key, [])]


def variante_por_slug(raca_slug: str, variante_slug: str) -> Optional[Dict[str, Any]]:
    key = (variante_slug or "").strip().lower()
    for row in listar_variantes_raca(raca_slug):
        if row.get("slug") == key:
            return row
    return None


def _normalizar_tipo_dano(tipo: str) -> str:
    t = (tipo or "").strip().lower()
    mapa = {
        "acid": "acido",
        "lightning": "eletricidade",
        "fire": "fogo",
        "cold": "frio",
        "poison": "veneno",
    }
    return mapa.get(t, t)


def tipo_dano_resistencia_racial(
    raca_slug: str,
    raca_variante_slug: Optional[str] = None,
) -> str:
    """Tipo de dano ao qual a raça/variante tem resistência (metade)."""
    raca = (raca_slug or "").strip().lower()
    if raca == "tiefling" and not raca_variante_slug:
        return "fogo"
    if raca == "draconato" and not raca_variante_slug:
        return ""
    var = variante_por_slug(raca, raca_variante_slug or "")
    if var:
        return _normalizar_tipo_dano(str(var.get("tipo_dano") or ""))
    if raca == "tiefling":
        return "fogo"
    return ""


def tracos_resumo_com_variante(
    tracos_base: str,
    raca_slug: str,
    raca_variante_slug: Optional[str] = None,
) -> str:
    var = variante_por_slug(raca_slug, raca_variante_slug or "")
    if not var:
        return tracos_base or ""
    tipo_pt = var.get("tipo_dano_pt") or var.get("tipo_dano") or ""
    extra = f"Linhagem {var.get('nome', '')}: resistência a {tipo_pt}."
    if tracos_base:
        return f"{tracos_base} {extra}"
    return extra


def validar_variante_racial(
    raca_slug: str,
    raca_variante_slug: Optional[str],
) -> None:
    if not raca_exige_variante(raca_slug):
        return
    if not (raca_variante_slug or "").strip():
        raise ValueError(f"Raça {raca_slug} exige escolha de linhagem/variante racial")
    if variante_por_slug(raca_slug, raca_variante_slug) is None:
        raise ValueError(f"Variante racial inválida: {raca_variante_slug}")
