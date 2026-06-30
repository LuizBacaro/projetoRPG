"""Defesa (CA) Tormenta 20 — base 10 + contribuição de Destreza."""

from __future__ import annotations

from typing import Any, List, Optional

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


def tem_armadura_pesada(itens_protecao: Optional[List[Any]]) -> bool:
    """True se algum item equipado for armadura pesada (v1.3: DES não entra na Defesa)."""
    for it in itens_protecao or []:
        if not isinstance(it, dict):
            continue
        if str(it.get("tipo", "") or "").strip().lower() == "pesada":
            return True
    return False


def soma_bonus_protecao(itens_protecao: Optional[List[Any]]) -> int:
    """Soma bônus de CA de armaduras, escudos e itens de proteção."""
    total = 0
    for it in itens_protecao or []:
        if isinstance(it, dict):
            total += int(it.get("bonus_ca", 0) or 0)
    return total


def defesa_total_v13(
    des_valor: int,
    itens_protecao: Optional[List[Any]] = None,
    *,
    outros_bonus: int = 0,
) -> int:
    """
    CA completa v1.3: 10 + valor de DES + bônus de armadura/escudo.
    Armadura pesada equipada: DES não se aplica (p.106 / RF-T07d).
    """
    bonus = soma_bonus_protecao(itens_protecao)
    des = 0 if tem_armadura_pesada(itens_protecao) else int(des_valor)
    return 10 + des + bonus + int(outros_bonus or 0)
