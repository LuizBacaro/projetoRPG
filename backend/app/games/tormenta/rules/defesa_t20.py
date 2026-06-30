"""Defesa (CA) Tormenta 20 — base 10 + contribuição de Destreza."""

from __future__ import annotations

from typing import Optional

from app.games.tormenta.rules.atributos_t20 import contribuicao_atributo_t20
from app.games.tormenta.rules.regra_versao_t20 import normalizar_regra_versao


def defesa_base_ca(
    des_valor: int,
    regra_versao: Optional[str] = None,
    *,
    outros_bonus: int = 0,
) -> int:
    """
    CA base sem armadura/escudo da lista de equipamentos.
    v1.3: 10 + valor de DES (+ outros). MB: 10 + modificador por faixa (+ outros).
    """
    des = contribuicao_atributo_t20(
        int(des_valor), normalizar_regra_versao(regra_versao)
    )
    return 10 + int(des) + int(outros_bonus or 0)
