"""Regras T20 — modificadores por faixa e custo de compra por pontos."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.atributos_t20 import (
    CHAVES_ATRIBUTO,
    METODOS_GERACAO_ATRIBUTOS,
    custo_total_compra_seis_atributos,
    custo_valor_atributo_compra,
    gerar_seis_valores_4d6,
    lista_pericias_com_atributo,
    modificador_atributo_t20,
    pontos_iniciais_compra,
    qualidade_geracao_4d6,
    validar_valores_base_4d6,
    valores_4d6_para_mapa,
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


def test_gerar_4d6_reproduzivel_com_seed() -> None:
    a = gerar_seis_valores_4d6(seed=42, exigir_qualidade_mb=True)
    b = gerar_seis_valores_4d6(seed=42, exigir_qualidade_mb=True)
    assert a == b
    assert all(3 <= v <= 18 for v in a)
    assert qualidade_geracao_4d6(a)


def test_qualidade_4d6_rejeita_baixa_soma_sem_quatorze() -> None:
    assert not qualidade_geracao_4d6([10, 10, 10, 10, 10, 10])
    assert qualidade_geracao_4d6([14, 10, 10, 10, 10, 10])
    assert qualidade_geracao_4d6([12, 12, 12, 12, 10, 10])


def test_validar_valores_base_4d6() -> None:
    validar_valores_base_4d6([14, 12, 11, 10, 9, 8])
    with pytest.raises(ValueError, match="3–18"):
        validar_valores_base_4d6([2, 12, 11, 10, 9, 8])
    with pytest.raises(ValueError, match="pelo menos"):
        validar_valores_base_4d6([10, 10, 10, 10, 10, 10])


def test_valores_4d6_para_mapa() -> None:
    m = valores_4d6_para_mapa([15, 14, 13, 12, 11, 10])
    assert list(m.keys()) == list(CHAVES_ATRIBUTO)
    assert m["for"] == 15
    assert m["car"] == 10


def test_metodos_geracao_contem_4d6() -> None:
    assert "4d6" in METODOS_GERACAO_ATRIBUTOS
