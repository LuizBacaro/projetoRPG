"""Defesa (CA) Tormenta 20 v1.3."""

from __future__ import annotations

from app.games.tormenta.rules.defesa_t20 import (
    defesa_base_ca,
    defesa_total_v13,
    soma_bonus_protecao,
    tem_armadura_pesada,
)


def test_defesa_v13_des_2() -> None:
    assert defesa_base_ca(2, "v13") == 12


def test_defesa_v13_des_0() -> None:
    assert defesa_base_ca(0, "v13") == 10


def test_defesa_mb_des_12() -> None:
    """MB: DES 12 → mod +1 → CA 11."""
    assert defesa_base_ca(12, "mb") == 11


def test_defesa_total_v13_sem_armadura() -> None:
    assert defesa_total_v13(3, []) == 13


def test_defesa_total_v13_leve_mais_escudo() -> None:
    itens = [
        {"nome": "Couro", "tipo": "leve", "bonus_ca": 2},
        {"nome": "Escudo", "tipo": "escudo", "bonus_ca": 1},
    ]
    assert defesa_total_v13(2, itens) == 15


def test_defesa_total_v13_pesada_sem_des() -> None:
    itens = [{"nome": "Peitoral", "tipo": "pesada", "bonus_ca": 8}]
    assert defesa_total_v13(4, itens) == 18


def test_defesa_total_v13_pesada_mais_escudo() -> None:
    itens = [
        {"nome": "Placas", "tipo": "pesada", "bonus_ca": 10},
        {"nome": "Escudo pesado", "tipo": "escudo", "bonus_ca": 2},
    ]
    assert defesa_total_v13(3, itens) == 22


def test_tem_armadura_pesada() -> None:
    assert tem_armadura_pesada([{"tipo": "leve"}]) is False
    assert tem_armadura_pesada([{"tipo": "pesada"}]) is True


def test_soma_bonus_protecao() -> None:
    itens = [{"bonus_ca": 6}, {"bonus_ca": 1}]
    assert soma_bonus_protecao(itens) == 7


def test_defesa_total_v13_ficha_com_armadura_e_escudo() -> None:
    from app.games.tormenta.rules.defesa_t20 import defesa_total_v13_ficha

    armaduras = [
        {"nome": "Couro", "tipo": "leve", "bonus_ca": 2},
        {"nome": "Broquel", "tipo": "escudo", "bonus_ca": 1, "empunhado": True},
    ]
    assert defesa_total_v13_ficha(2, armaduras, []) == 15


def test_ca_efetiva_personagem_v13_com_armadura() -> None:
    from app.games.tormenta.rules.defesa_t20 import ca_efetiva_personagem

    fj = {
        "regra_versao": "v13",
        "armaduras_protecao": [
            {"nome": "Couro", "tipo": "leve", "bonus_ca": 2},
            {"nome": "Broquel", "tipo": "escudo", "bonus_ca": 1, "empunhado": True},
        ],
    }
    assert ca_efetiva_personagem(des_valor=3, ca=13, ficha_json=fj) == 16


def test_ca_efetiva_personagem_mb_soma_itens() -> None:
    from app.games.tormenta.rules.defesa_t20 import ca_efetiva_personagem

    fj = {
        "armaduras_protecao": [{"nome": "Couro", "tipo": "leve", "bonus_ca": 2}],
    }
    assert ca_efetiva_personagem(des_valor=12, ca=11, ficha_json=fj) == 13
