"""Testes RF-T14 — agregador de melhorias TS → perícia."""

from __future__ import annotations

from app.games.tormenta.rules.bonus_pericias_itens_t20 import (
    agregar_bonus_pericia_itens,
    aplicar_agregado_em_totais,
    slug_pericia_nome,
)


def test_slug_pericia_nome_acentos():
    assert slug_pericia_nome("Enganação") == "enganacao"
    assert slug_pericia_nome("Ofício") == "oficio"


def test_agregar_banhado_a_ouro_diplomacia():
    agg = agregar_bonus_pericia_itens(
        pericia_slug="diplomacia",
        itens=[{"melhorias": ["banhado_a_ouro"], "bonus_ativo": True}],
    )
    assert agg["outros"] == 2
    assert agg["bonus_uso"] == 0
    assert any(f["melhoria"] == "banhado_a_ouro" for f in agg["fontes"])


def test_agregar_macabro_intimidacao_e_pen_diplomacia():
    a = agregar_bonus_pericia_itens(
        pericia_slug="intimidacao",
        itens=[{"melhorias": ["macabro"]}],
    )
    assert a["outros"] == 2
    b = agregar_bonus_pericia_itens(
        pericia_slug="diplomacia",
        itens=[{"melhorias": ["macabro"]}],
    )
    assert b["outros"] == -2


def test_agregar_discreto_ocultar_so_no_uso():
    sem = agregar_bonus_pericia_itens(
        pericia_slug="ladinagem",
        uso_id=None,
        itens=[{"melhorias": ["discreto"]}],
    )
    assert sem["outros"] == 0
    assert sem["bonus_uso"] == 0
    com = agregar_bonus_pericia_itens(
        pericia_slug="ladinagem",
        uso_id="ocultar",
        itens=[{"melhorias": ["discreto"]}],
    )
    assert com["bonus_uso"] == 5
    assert com["outros"] == 0


def test_agregar_ignora_bonus_inativo():
    agg = agregar_bonus_pericia_itens(
        pericia_slug="enganacao",
        itens=[{"melhorias": ["cravejado_de_gemas"], "bonus_ativo": False}],
    )
    assert agg["outros"] == 0


def test_aplicar_agregado_nao_muta_ficha_em_double_count_conceitual():
    totais = aplicar_agregado_em_totais(
        outros_ficha=1,
        bonus_uso_ficha=2,
        agregado={"outros": 2, "bonus_uso": 5},
    )
    assert totais["outros"] == 3
    assert totais["bonus_uso"] == 7
    assert totais["bonus_itens"] == 2
    assert totais["bonus_uso_itens"] == 5
