"""Limites vestido/empunhado — Tormenta 20 v1.3 (RF-T07h-1)."""

from __future__ import annotations

from app.games.tormenta.rules.defesa_t20 import soma_bonus_protecao_ficha
from app.games.tormenta.rules.limites_equipamento_v13_t20 import (
    MAX_EMPUNHADOS,
    MAX_VESTIDOS_MECANICOS,
    aplicar_limites_equipamento,
    aplicar_limites_ficha,
    resumo_limites_equipamento,
    resumo_limites_ficha,
    soma_bonus_ca_ativos,
    validar_adicionar_equipamento,
)


def _armadura_leve(nome: str, bonus: int = 1) -> dict:
    return {"nome": nome, "tipo": "leve", "bonus_ca": bonus, "penalidade": 0}


def test_quinto_vestido_bonus_inativo() -> None:
    itens = [_armadura_leve(f"Armadura {i}", i + 1) for i in range(5)]
    marcados = aplicar_limites_equipamento(itens)
    assert len(marcados) == 5
    assert (
        sum(1 for it in marcados if it.get("bonus_ativo") is True)
        == MAX_VESTIDOS_MECANICOS
    )
    assert marcados[4]["bonus_ativo"] is False
    assert soma_bonus_ca_ativos(itens) == 1 + 2 + 3 + 4


def test_terceiro_empunhado_inativo() -> None:
    itens = [
        {"nome": "Escudo A", "tipo": "escudo", "bonus_ca": 1, "penalidade": -1},
        {"nome": "Escudo B", "tipo": "escudo", "bonus_ca": 1, "penalidade": -1},
        {"nome": "Escudo C", "tipo": "escudo", "bonus_ca": 2, "penalidade": -2},
    ]
    marcados = aplicar_limites_equipamento(itens)
    assert marcados[2]["bonus_ativo"] is False
    assert soma_bonus_ca_ativos(itens) == 2


def test_defesa_respeita_limites() -> None:
    itens = [_armadura_leve(f"A{i}", 2) for i in range(5)]
    assert soma_bonus_ca_ativos(itens) == 8
    assert soma_bonus_protecao_ficha(itens) == 8


def test_escudo_mais_duas_armas_empunhadas_terceira_inativa() -> None:
    armaduras = [
        {"nome": "Escudo leve", "tipo": "escudo", "bonus_ca": 1, "penalidade": -1},
    ]
    ataques = [
        {
            "nome": "Espada longa",
            "dano": "1d8",
            "bonus_ataque": "+5",
            "empunhado": True,
        },
        {"nome": "Adaga", "dano": "1d4", "bonus_ataque": "+5", "empunhado": True},
        {"nome": "Maça", "dano": "1d6", "bonus_ataque": "+4", "empunhado": True},
    ]
    res = resumo_limites_ficha(armaduras, ataques)
    assert res["empunhados"] == 4
    assert res["excedeu_empunhados"] is True
    marcados = aplicar_limites_ficha(armaduras, ataques)
    assert marcados["armaduras"][0]["bonus_ativo"] is True
    assert marcados["ataques"][0]["bonus_ativo"] is True
    assert marcados["ataques"][1]["bonus_ativo"] is False
    assert marcados["ataques"][2]["bonus_ativo"] is False


def test_validar_escudo_considera_ataques_empunhados() -> None:
    armaduras: list = []
    ataques = [
        {"nome": "Espada", "dano": "1d8", "bonus_ataque": "+5", "empunhado": True},
        {"nome": "Adaga", "dano": "1d4", "bonus_ataque": "+5", "empunhado": True},
    ]
    novo = {"nome": "Escudo", "tipo": "escudo", "bonus_ca": 1, "penalidade": -1}
    val = validar_adicionar_equipamento(armaduras, novo, ataques=ataques)
    assert val["resumo"]["empunhados"] == 3
    assert val["aviso"]


def test_validar_adicionar_quinto_vestido_aviso() -> None:
    atuais = [_armadura_leve(f"A{i}") for i in range(4)]
    novo = _armadura_leve("Quinta")
    val = validar_adicionar_equipamento(atuais, novo)
    assert val["permitir"] is True
    assert val["resumo"]["excedeu_vestidos"] is True
    assert val["aviso"]


def test_resumo_contadores() -> None:
    itens = [
        _armadura_leve("Couro"),
        {"nome": "Escudo", "tipo": "escudo", "bonus_ca": 1, "penalidade": -1},
    ]
    res = resumo_limites_equipamento(itens)
    assert res["vestidos"] == 1
    assert res["empunhados"] == 1
    assert res["max_vestidos"] == MAX_VESTIDOS_MECANICOS
    assert res["max_empunhados"] == MAX_EMPUNHADOS
