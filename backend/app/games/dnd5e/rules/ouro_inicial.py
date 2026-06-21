"""Ouro inicial por classe — rolagem e sincronização na ficha."""

from __future__ import annotations

import random
from typing import Any, Dict, List, Optional

from app.games.dnd5e.data.ouro_inicial_catalogo import (
    OURO_INICIAL_POR_CLASSE,
    formula_ouro_inicial,
)
from app.games.dnd5e.rules.classes import CLASSE_SLUGS_VALIDOS


def spec_ouro_inicial(classe_slug: str) -> Optional[Dict[str, int]]:
    key = (classe_slug or "").strip().lower()
    spec = OURO_INICIAL_POR_CLASSE.get(key)
    return dict(spec) if spec else None


def rolar_ouro_inicial_classe(
    classe_slug: str,
    *,
    rng: Optional[random.Random] = None,
) -> Dict[str, Any]:
    key = (classe_slug or "").strip().lower()
    if key not in CLASSE_SLUGS_VALIDOS:
        raise ValueError(f"Classe inválida: {classe_slug}")
    spec = OURO_INICIAL_POR_CLASSE[key]
    r = rng or random.Random()
    dados: List[int] = [r.randint(1, spec["faces"]) for _ in range(spec["dados"])]
    soma = sum(dados)
    total = soma * int(spec["multiplicador"])
    return {
        "classe_slug": key,
        "total": total,
        "dados": dados,
        "soma_dados": soma,
        "multiplicador": int(spec["multiplicador"]),
        "formula": formula_ouro_inicial(key),
    }


def sincronizar_ouro_classe_na_ficha(
    ficha: Dict[str, Any],
    *,
    rng: Optional[random.Random] = None,
    forcar: bool = False,
    total_fixo: Optional[int] = None,
) -> Dict[str, Any]:
    """
    Aplica ouro inicial da classe ao inventário.
    Substitui o valor anterior da mesma origem ao trocar de classe.
    """
    out = dict(ficha or {})
    slug_atual = (out.get("classe_slug") or "").strip().lower() or None
    slug_aplicado = (out.get("classe_ouro_slug") or "").strip().lower() or None

    if (
        not forcar
        and slug_atual == slug_aplicado
        and out.get("ouro_classe_aplicado") is not None
    ):
        return out

    inv = dict(out.get("inventario") or {})
    ouro_po = float(inv.get("ouro_po") or 0)
    ouro_classe_ant = int(out.get("ouro_classe_aplicado") or 0)
    ouro_po = max(0.0, ouro_po - ouro_classe_ant)

    out.pop("ouro_classe_rolagem", None)
    out.pop("ouro_classe_formula", None)
    out["ouro_classe_aplicado"] = 0
    out["classe_ouro_slug"] = slug_atual

    if slug_atual:
        if total_fixo is not None:
            roll = {
                "classe_slug": slug_atual,
                "total": max(0, int(total_fixo)),
                "dados": [],
                "soma_dados": max(0, int(total_fixo)),
                "multiplicador": 1,
                "formula": formula_ouro_inicial(slug_atual),
            }
        else:
            roll = rolar_ouro_inicial_classe(slug_atual, rng=rng)
        out["ouro_classe_aplicado"] = int(roll["total"])
        out["ouro_classe_rolagem"] = list(roll.get("dados") or [])
        out["ouro_classe_formula"] = str(roll.get("formula") or "")
        ouro_po += float(roll["total"])
    else:
        out.pop("classe_ouro_slug", None)

    inv["ouro_po"] = ouro_po
    out["inventario"] = inv
    return out
