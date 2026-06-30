"""Carga e espaços Tormenta 20 v1.3."""

from __future__ import annotations

from app.games.tormenta.rules.carga_t20 import (
    espacos_moedas,
    espacos_por_item,
    estado_carga,
    limite_carga_for,
    limite_carga_maximo,
    preview_carga_v13,
)


def test_limite_for_2() -> None:
    assert limite_carga_for(2) == 14
    assert limite_carga_maximo(2) == 28


def test_limite_for_negativa() -> None:
    assert limite_carga_for(-2) == 8


def test_limite_for_zero() -> None:
    assert limite_carga_for(0) == 10


def test_mochila_zero_espacos() -> None:
    assert espacos_por_item({"nome": "Mochila"}) == 0.0


def test_armadura_pesada_cinco() -> None:
    assert espacos_por_item({"nome": "Armadura de placas", "tipo": "pesada"}) == 5.0


def test_armadura_leve_dois() -> None:
    assert espacos_por_item({"nome": "Armadura de couro", "tipo": "leve"}) == 2.0


def test_escudo_pesado_dois() -> None:
    assert espacos_por_item({"nome": "Escudo pesado de aço", "tipo": "escudo"}) == 2.0


def test_pocao_meio_espaco() -> None:
    assert espacos_por_item({"nome": "Poção de cura (frasco)"}) == 0.5


def test_moedas_espacos() -> None:
    assert espacos_moedas(999) == 0
    assert espacos_moedas(1000) == 1
    assert espacos_moedas(2500) == 2


def test_estado_sobrecarga() -> None:
    assert estado_carga(2, 14) == "normal"
    assert estado_carga(2, 15) == "sobrecarregado"
    assert estado_carga(2, 29) == "acima_maximo"


def test_preview_kit_inicial() -> None:
    itens = [
        {"nome": "Mochila", "quantidade": 1},
        {"nome": "Saco de dormir", "quantidade": 1},
        {"nome": "Roupas de viajante", "quantidade": 1},
        {"nome": "Armadura de couro", "tipo": "leve", "quantidade": 1},
        {"nome": "Espada longa", "quantidade": 1},
    ]
    prev = preview_carga_v13(for_valor=2, itens=itens, moedas_total=500)
    assert prev["limite"] == 14
    assert prev["espacos_itens"] == 5.0
    assert prev["estado"] == "normal"
