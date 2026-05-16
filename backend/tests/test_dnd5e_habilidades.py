"""Regras D&D 5E — habilidades."""

import pytest

from app.games.dnd5e.rules.habilidades import (
    AbilityScores,
    PersonagemHabilidades,
    calcular_bonus_proficiencia,
    calcular_modificador,
    validar_valor_habilidade,
)


def test_calcular_modificador_16() -> None:
    assert calcular_modificador(16) == 3


@pytest.mark.parametrize(
    "nivel,esperado",
    [(1, 2), (4, 2), (5, 3), (9, 4), (13, 5), (17, 6), (20, 6)],
)
def test_bonus_proficiencia(nivel: int, esperado: int) -> None:
    assert calcular_bonus_proficiencia(nivel) == esperado


def test_validacao_habilidade_fora_faixa() -> None:
    with pytest.raises(ValueError):
        validar_valor_habilidade(0)
    with pytest.raises(ValueError):
        validar_valor_habilidade(26)


def test_personagem_getters_modificador() -> None:
    p = PersonagemHabilidades(
        abilities=AbilityScores(
            strength=16,
            dexterity=10,
            constitution=14,
            intelligence=12,
            wisdom=8,
            charisma=18,
        ),
        nivel=5,
    )
    assert p.strength_mod == 3
    assert p.dexterity_mod == 0
    assert p.constitution_mod == 2
    assert p.bonus_proficiencia == 3
