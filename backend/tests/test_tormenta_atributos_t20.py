"""Regras T20 — modificadores por faixa e custo de compra por pontos."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.atributos_t20 import (
    custo_total_compra_seis_atributos,
    custo_valor_atributo_compra,
    lista_pericias_com_atributo,
    modificador_atributo_t20,
    pontos_iniciais_compra,
)


@pytest.mark.parametrize(
    "valor,esperado",
    [
        (1, -5),
        (2, -4),
        (8, -1),
        (10, 0),
        (11, 0),
        (12, 1),
        (18, 4),
        (20, 5),
        (26, 8),
    ],
)
def test_modificador_atributo_t20(valor: int, esperado: int) -> None:
    assert modificador_atributo_t20(valor) == esperado


def test_modificador_limite_inferior() -> None:
    assert modificador_atributo_t20(-99) == modificador_atributo_t20(1)


def test_custo_compra_valores_conhecidos() -> None:
    assert custo_valor_atributo_compra(8) == -2
    assert custo_valor_atributo_compra(10) == 0
    assert custo_valor_atributo_compra(18) == 14
    assert custo_valor_atributo_compra(7) is None


def test_pontos_iniciais_compra() -> None:
    assert pontos_iniciais_compra() == 20


def test_custo_total_todos_dez() -> None:
    """Seis atributos 10 = 0 pontos cada."""
    assert custo_total_compra_seis_atributos(10, 10, 10, 10, 10, 10) == 0


def test_custo_total_fora_tabela() -> None:
    assert custo_total_compra_seis_atributos(10, 10, 10, 10, 10, 7) is None


def test_custo_total_quatro_dezoito() -> None:
    assert custo_total_compra_seis_atributos(18, 18, 18, 18, 10, 10) == 56


def test_lista_pericias_tamanho_e_primeira() -> None:
    lst = lista_pericias_com_atributo()
    assert len(lst) == 32
    assert lst[0]["nome"] == "Acrobacia"
    assert lst[0]["atributo"] == "des"
    assert lst[0]["somente_treinado"] is False
    assert lst[0]["penalidade_armadura"] is True
    assert lst[1]["nome"] == "Adestramento"
    assert lst[1]["somente_treinado"] is True
    assert lst[1]["penalidade_armadura"] is False
    assert lst[10]["nome"] == "Furtividade"
    assert lst[10]["penalidade_armadura"] is True
    assert lst[17]["nome"] == "Ladinagem"
    assert lst[17]["penalidade_armadura"] is True
    assert lst[21]["nome"] == "Ofício"
    assert lst[21]["somente_treinado"] is False
    assert lst[21]["penalidade_armadura"] is False
    assert lst[-2]["nome"] == "—"
