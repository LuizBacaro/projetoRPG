"""Traços raciais mecânicos Tormenta 20 — MB e v1.3."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_TRACOS_MB_JSON = _DATA_DIR / "tracos_mecanicos_mb.json"
_TRACOS_V13_JSON = _DATA_DIR / "tracos_mecanicos_v13.json"

# Legado MB → v1.3 quando ficha antiga usa slug MB no motor v13.
_SLUG_ALIASES_V13: Dict[str, str] = {
    "halfling": "hynne",
}


def _resolver_slug(slug: str, regra_versao: str) -> str:
    s = str(slug or "").strip().lower()
    if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13:
        return _SLUG_ALIASES_V13.get(s, s)
    return s


@lru_cache(maxsize=2)
def _carregar_tracos(regra_versao: str = REGRA_VERSAO_MB) -> Dict[str, Any]:
    path = (
        _TRACOS_V13_JSON
        if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13
        else _TRACOS_MB_JSON
    )
    if not path.is_file():
        return {"racas": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def tracos_mecanicos_por_slug(
    slug: str,
    regra_versao: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Efeitos mecânicos da raça ou None se slug desconhecido."""
    rv = normalizar_regra_versao(regra_versao)
    s = _resolver_slug(slug, rv)
    if not s:
        return None
    racas = _carregar_tracos(rv).get("racas") or {}
    if not isinstance(racas, dict):
        return None
    row = racas.get(s)
    if not isinstance(row, dict):
        return None
    return dict(row)


def humano_versatil_pericias_extra(humano_versatil: Optional[str]) -> int:
    """Humano v1.3 Versátil: 2 perícias (padrão) ou 1 perícia + 1 poder geral."""
    v = str(humano_versatil or "").strip().lower()
    if v == "pericia_poder":
        return 1
    return 2


def pericias_treinadas_extra_de_tracos(
    slug: str,
    regra_versao: Optional[str] = None,
    *,
    humano_versatil: Optional[str] = None,
) -> int:
    rv = normalizar_regra_versao(regra_versao)
    s = _resolver_slug(slug, rv)
    if rv == REGRA_VERSAO_V13 and s == "humano":
        return humano_versatil_pericias_extra(humano_versatil)
    row = tracos_mecanicos_por_slug(slug, rv)
    if not row:
        return 0
    return int(row.get("pericias_treinadas_extra", 0) or 0)


def preview_tracos_raciais(
    slug: str,
    *,
    pericias_nomes: Optional[List[str]] = None,
    regra_versao: Optional[str] = None,
    humano_versatil: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Resumo de bônus raciais aplicáveis para a ficha.
    `pericias_nomes` opcional: lista de nomes de perícias para mapear bônus por nome.
    """
    rv = normalizar_regra_versao(regra_versao)
    s = _resolver_slug(slug, rv)
    row = tracos_mecanicos_por_slug(slug, rv)
    if not row:
        return {
            "slug": s or slug,
            "encontrado": False,
            "regra_versao": rv,
            "tamanho": None,
            "deslocamento_m": None,
            "ca_bonus": 0,
            "ca_vs_grande_ou_maior": 0,
            "ataque_bonus": 0,
            "furtividade_bonus": 0,
            "fortitude_bonus": 0,
            "reflexos_bonus": 0,
            "vontade_bonus": 0,
            "pericias_bonus": {},
            "pericias_treinadas_extra": 0,
        }

    per_map = row.get("pericias_bonus") or {}
    if not isinstance(per_map, dict):
        per_map = {}

    out_per: Dict[str, int] = {}
    if pericias_nomes:
        for nome in pericias_nomes:
            n = str(nome or "").strip()
            if n and n in per_map:
                out_per[n] = int(per_map[n])
    else:
        out_per = {str(k): int(v) for k, v in per_map.items()}

    extra = pericias_treinadas_extra_de_tracos(
        slug, rv, humano_versatil=humano_versatil
    )

    return {
        "slug": s,
        "encontrado": True,
        "regra_versao": rv,
        "tamanho": row.get("tamanho"),
        "deslocamento_m": row.get("deslocamento_m"),
        "ca_bonus": int(row.get("ca_bonus", 0) or 0),
        "ca_vs_grande_ou_maior": int(row.get("ca_vs_grande_ou_maior", 0) or 0),
        "ataque_bonus": int(row.get("ataque_bonus", 0) or 0),
        "furtividade_bonus": int(row.get("furtividade_bonus", 0) or 0),
        "fortitude_bonus": int(row.get("fortitude_bonus", 0) or 0),
        "reflexos_bonus": int(row.get("reflexos_bonus", 0) or 0),
        "vontade_bonus": int(row.get("vontade_bonus", 0) or 0),
        "pericias_bonus": out_per,
        "pericias_treinadas_extra": extra,
    }
