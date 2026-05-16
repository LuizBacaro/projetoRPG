"""Regras D&D 5E — combate."""

from app.games.dnd5e.rules.combate import (
    ArmaCombate,
    Combatente,
    RodadaCombate,
    StatusVida,
    ataque_atinge_ca,
    calcular_dano,
    calcular_iniciativa,
    registrar_teste_morte,
    verificar_morte,
)


def test_iniciativa_ordenacao() -> None:
    g = Combatente("g", "Guerreiro", hp=30, max_hp=30, ac=16, dex_mod=1, str_mod=3)
    gob = Combatente("b", "Goblin", hp=8, max_hp=8, ac=15, dex_mod=2, str_mod=0)
    rodada = RodadaCombate(combatentes=[g, gob])
    rodada.ordenar_por_iniciativa(rolagens={"g": 12, "b": 8})
    assert rodada.ordem_iniciativa[0].nome == "Guerreiro"
    assert rodada.ordem_iniciativa[0].iniciativa_rolagem == 13


def test_ataque_atinge_ca() -> None:
    assert ataque_atinge_ca(3, 2, 16, rolagem_d20=16) is True
    assert ataque_atinge_ca(3, 2, 16, rolagem_d20=10) is False


def test_critico_multiplica_dados() -> None:
    arma = ArmaCombate(dano="1d8")
    normal = calcular_dano(arma, 3, is_critico=False, rng=lambda a, b: 6)
    crit = calcular_dano(arma, 3, is_critico=True, rng=lambda a, b: 6)
    assert crit >= normal
    assert crit == max(1, 6 + 6 + 3)


def test_morte_tres_falhas() -> None:
    c = Combatente("x", "Alvo", hp=0, max_hp=10, ac=10)
    assert verificar_morte(0, 0, 0) == StatusVida.INCONSCIENTE
    c.death_failures = 2
    status = registrar_teste_morte(c, 5)
    assert status == StatusVida.MORTO
    assert c.death_failures >= 3


def test_calcular_iniciativa() -> None:
    assert calcular_iniciativa(2, rolagem_d20=10) == 12
