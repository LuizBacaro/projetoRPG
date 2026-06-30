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
    """Soma bônus de CA de armaduras, escudos e itens de proteção (respeita limites v1.3)."""
    from app.games.tormenta.rules.limites_equipamento_v13_t20 import (
        soma_bonus_ca_ativos,
    )

    return soma_bonus_ca_ativos(itens_protecao)


def soma_bonus_protecao_ficha(
    itens_protecao: Optional[List[Any]],
    ataques: Optional[List[Any]] = None,
) -> int:
    """CA ativa na ficha (escudos competem com armas empunhadas pelo limite de 2)."""
    from app.games.tormenta.rules.limites_equipamento_v13_t20 import soma_bonus_ca_ficha

    return soma_bonus_ca_ficha(itens_protecao, ataques)


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


def defesa_total_v13_ficha(
    des_valor: int,
    itens_protecao: Optional[List[Any]] = None,
    ataques: Optional[List[Any]] = None,
    *,
    outros_bonus: int = 0,
) -> int:
    """
    CA v1.3 na ficha/arena: limites vestido/empunhado (escudo vs armas).
    """
    from app.games.tormenta.rules.limites_equipamento_v13_t20 import soma_bonus_ca_ficha

    bonus = soma_bonus_ca_ficha(itens_protecao, ataques)
    des = 0 if tem_armadura_pesada(itens_protecao) else int(des_valor)
    return 10 + des + bonus + int(outros_bonus or 0)


def _listas_protecao_ficha(ficha_json: Optional[Any]) -> tuple[List[Any], List[Any]]:
    fj = ficha_json if isinstance(ficha_json, dict) else {}
    arm = fj.get("armaduras_protecao")
    atq = fj.get("ataques")
    return (
        list(arm) if isinstance(arm, list) else [],
        list(atq) if isinstance(atq, list) else [],
    )


def ca_efetiva_personagem(
    *,
    des_valor: int,
    ca: int,
    ficha_json: Optional[Any] = None,
) -> int:
    """
    CA de combate: base salva na ficha + armaduras/escudos equipados (RF-T07d-1).
    """
    from app.games.tormenta.rules.limites_equipamento_v13_t20 import soma_bonus_ca_ficha
    from app.games.tormenta.rules.regra_versao_t20 import (
        REGRA_VERSAO_V13,
        regra_versao_de_ficha,
    )

    armaduras, ataques = _listas_protecao_ficha(ficha_json)
    rv = regra_versao_de_ficha(ficha_json if isinstance(ficha_json, dict) else {})
    if rv == REGRA_VERSAO_V13:
        return defesa_total_v13_ficha(int(des_valor), armaduras, ataques)
    bonus = soma_bonus_ca_ficha(armaduras, ataques)
    return int(ca or 10) + bonus
