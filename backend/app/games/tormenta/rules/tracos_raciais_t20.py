"""Traços raciais mecânicos MB — bônus a CA, resistências e perícias."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_TRACOS_JSON = _DATA_DIR / "tracos_mecanicos_mb.json"


@lru_cache(maxsize=1)
def _carregar_tracos() -> Dict[str, Any]:
    if not _TRACOS_JSON.is_file():
        return {"racas": {}}
    return json.loads(_TRACOS_JSON.read_text(encoding="utf-8"))


def tracos_mecanicos_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    """Efeitos mecânicos da raça MB ou None se slug desconhecido."""
    s = str(slug or "").strip().lower()
    if not s:
        return None
    racas = _carregar_tracos().get("racas") or {}
    if not isinstance(racas, dict):
        return None
    row = racas.get(s)
    if not isinstance(row, dict):
        return None
    return dict(row)


def preview_tracos_raciais(
    slug: str,
    *,
    pericias_nomes: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Resumo de bônus raciais aplicáveis para a ficha.
    `pericias_nomes` opcional: lista de nomes de perícias para mapear bônus por nome.
    """
    row = tracos_mecanicos_por_slug(slug)
    if not row:
        return {
            "slug": slug,
            "encontrado": False,
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

    return {
        "slug": slug,
        "encontrado": True,
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
    }
