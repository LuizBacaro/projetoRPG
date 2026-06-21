"""Ouro inicial por classe (PHB Cap. 5) — fórmulas de rolagem."""

from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class OuroInicialSpec(TypedDict):
    dados: int
    faces: int
    multiplicador: int


# Monge: 5d4 gp (sem ×10). Demais classes usam Nd4 × 10.
OURO_INICIAL_POR_CLASSE: Dict[str, OuroInicialSpec] = {
    "barbaro": {"dados": 2, "faces": 4, "multiplicador": 10},
    "bardo": {"dados": 5, "faces": 4, "multiplicador": 10},
    "bruxo": {"dados": 4, "faces": 4, "multiplicador": 10},
    "clerigo": {"dados": 5, "faces": 4, "multiplicador": 10},
    "druida": {"dados": 2, "faces": 4, "multiplicador": 10},
    "feiticeiro": {"dados": 3, "faces": 4, "multiplicador": 10},
    "guerreiro": {"dados": 5, "faces": 4, "multiplicador": 10},
    "ladino": {"dados": 4, "faces": 4, "multiplicador": 10},
    "mago": {"dados": 4, "faces": 4, "multiplicador": 10},
    "monge": {"dados": 5, "faces": 4, "multiplicador": 1},
    "paladino": {"dados": 5, "faces": 4, "multiplicador": 10},
    "patrulheiro": {"dados": 5, "faces": 4, "multiplicador": 10},
}


def formula_ouro_inicial(classe_slug: str) -> str:
    spec = OURO_INICIAL_POR_CLASSE.get((classe_slug or "").strip().lower())
    if not spec:
        return "—"
    n, f, m = spec["dados"], spec["faces"], spec["multiplicador"]
    if m == 1:
        return f"{n}d{f} gp"
    return f"{n}d{f} × {m} gp"
