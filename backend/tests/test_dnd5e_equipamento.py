"""Regras D&D 5E — equipamento."""

from app.games.dnd5e.rules.equipamento import (
    Arma,
    Armadura,
    Escudo,
    Item,
    calcular_ac_total,
    calcular_dano_arma,
    calcular_penalidade_encargo,
    calcular_peso_total,
    validar_peso_maximo,
)


def test_ac_com_escudo() -> None:
    arm = Armadura("cota", "Cota de Malha", tipo_armadura="media", ca=14)
    esc = Escudo("esc", "Escudo", bonus_ac=2)
    ac = calcular_ac_total(arm, esc, dex_mod=3)
    assert ac == 14 + 2 + 2


def test_dano_arma_inclui_mod() -> None:
    arma = Arma("espada", "Espada Longa", dano="1d8")
    assert calcular_dano_arma(arma, 3) == "1d8+3"


def test_encargo_reduz_velocidade() -> None:
    itens = [Item("i", "Carga", peso=200, quantidade=1)]
    peso = calcular_peso_total(itens)
    assert calcular_penalidade_encargo(peso, forca=10) == 3
    assert validar_peso_maximo(peso, forca=10) is True
