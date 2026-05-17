"""Testes unitários das regras de companheiro animal D&D 3.5."""

from app.games.dnd35.rules.companheiro_animal import (
    calcular_estatisticas,
    elegibilidade_companheiro,
    hd_bonus,
    truques_bonus_qtd,
)


def test_elegibilidade_druida_e_ranger():
    ok, _, ne = elegibilidade_companheiro("Druida", 7)
    assert ok and ne == 7
    ok2, _, ne2 = elegibilidade_companheiro("Ranger", 10)
    assert ok2 and ne2 == 7
    ok3, motivo, _ = elegibilidade_companheiro("Ranger", 3)
    assert not ok3 and "4" in motivo


def test_elegibilidade_multiclasse_e_classe_com_nivel():
    ok, _, ne = elegibilidade_companheiro("Druida / Guerreiro", 7)
    assert ok and ne == 7
    ok2, _, ne2 = elegibilidade_companheiro("Guerreiro 5 / Druida 7", 12)
    assert ok2 and ne2 == 7
    ok3, _, ne3 = elegibilidade_companheiro("Druida 7", 7)
    assert ok3 and ne3 == 7
    ok4, _, ne4 = elegibilidade_companheiro("Ranger 4", 4)
    assert ok4 and ne4 == 1


def test_hd_bonus_formula():
    assert hd_bonus(1) == 0
    assert hd_bonus(3) == 1
    assert hd_bonus(7) == 2


def test_truques_bonus():
    assert truques_bonus_qtd(1) == 1
    assert truques_bonus_qtd(6) == 2
    assert truques_bonus_qtd(10) == 4


def test_calcular_lobo_druida_7():
    deriv = calcular_estatisticas(
        nivel_efetivo=7,
        hd_base=2,
        atributos_base={
            "forca": 13,
            "destreza": 15,
            "constituicao": 13,
            "inteligencia": 2,
            "sabedoria": 12,
            "carisma": 6,
        },
        bonus_atributos={"forca": 2, "constituicao": 2},
        armadura_natural_base=2,
    )
    assert deriv["hd_total"] == 4
    assert deriv["bab"] == 4
    assert deriv["fortitude"] == 4
    assert deriv["truques_bonus"] == 3
