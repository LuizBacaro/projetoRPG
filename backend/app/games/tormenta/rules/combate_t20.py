"""Combate Tormenta 20 — rolagens de iniciativa, ataque e dano; condições v1.3."""

from __future__ import annotations

import random
import re
from typing import Any, Dict, List, Optional, Tuple

from app.games.tormenta.rules.condicoes_t20 import modificadores_de_condicoes


def modificadores_de_condicoes_mb(
    rotulos: Optional[List[str]],
) -> Dict[str, int]:
    """Alias — delega ao catálogo v1.3 (RF-T05-v13)."""
    return modificadores_de_condicoes(rotulos)


def rolar_dado_formula(
    formula: str, seed: Optional[int] = None
) -> Tuple[int, List[int]]:
    """
    Rola fórmula simples NdM (+/-X opcional).
    Ex.: '1d8', '2d6+3', '1d20'.
    """
    rng = random.Random(seed) if seed is not None else random
    f = str(formula or "").strip().lower().replace(" ", "")
    if not f:
        return 0, []
    m = re.match(r"^(\d+)d(\d+)([+-]\d+)?$", f)
    if not m:
        return 0, []
    n = int(m.group(1))
    faces = int(m.group(2))
    mod = int(m.group(3) or 0)
    rolls = [rng.randint(1, faces) for _ in range(n)]
    return sum(rolls) + mod, rolls


def rolar_iniciativa(
    mod_destreza: int,
    *,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed) if seed is not None else random
    d20 = rng.randint(1, 20)
    mod = int(mod_destreza)
    return {"d20": d20, "modificador": mod, "total": d20 + mod}


def rolar_ataque(
    bab: int,
    mod_atributo: int,
    *,
    bonus_arma: int = 0,
    penalidades: int = 0,
    modificador_condicoes: int = 0,
    ca_alvo: int,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    rng = random.Random(seed) if seed is not None else random
    d20 = rng.randint(1, 20)
    bonus = (
        int(bab)
        + int(mod_atributo)
        + int(bonus_arma)
        - int(penalidades)
        + int(modificador_condicoes)
    )
    total = d20 + bonus
    ca = int(ca_alvo)
    acertou = total >= ca
    ameaca_critica = d20 == 20 or d20 >= 19
    return {
        "d20": d20,
        "bonus": bonus,
        "total": total,
        "ca_alvo": ca,
        "acertou": acertou,
        "ameaca_critica": ameaca_critica,
        "falha_critica": d20 == 1,
    }


def rolar_dano(
    formula_dano: str,
    mod_atributo: int = 0,
    *,
    confirmar_critico: bool = False,
    multiplicador_critico: int = 2,
    seed: Optional[int] = None,
) -> Dict[str, Any]:
    base, rolls = rolar_dado_formula(formula_dano, seed=seed)
    mod = int(mod_atributo)
    total = max(1, base + mod)
    if confirmar_critico:
        extra, rolls2 = rolar_dado_formula(
            formula_dano, seed=None if seed is None else seed + 1
        )
        total = max(1, (base + extra + mod * 2) * (multiplicador_critico // 2))
        rolls = rolls + rolls2
    return {
        "formula": formula_dano,
        "rolagens": rolls,
        "modificador": mod,
        "dano": total,
        "critico": confirmar_critico,
    }
