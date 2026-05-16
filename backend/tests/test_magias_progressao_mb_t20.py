"""Regras MB — círculo máximo e tipo de lista por classe."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.magias_progressao_mb_t20 import (
    circulo_maximo_magias_lancaveis_mb,
    tipo_lista_magias_por_classe_mb,
)


@pytest.mark.parametrize(
    "slug,nivel,esperado",
    [
        ("clerigo", 1, 1),
        ("clerigo", 2, 1),
        ("clerigo", 3, 2),
        ("clerigo", 4, 2),
        ("mago", 1, 1),
        ("mago", 2, 2),
        ("mago", 3, 2),
        ("paladino", 4, 0),
        ("paladino", 5, 1),
        ("paladino", 8, 1),
        ("paladino", 9, 2),
        ("bardo", 3, 1),
        ("bardo", 4, 2),
        ("bardo", 16, 6),
        ("bardo", 20, 6),
    ],
)
def test_circulo_maximo_magias_mb(slug, nivel, esperado):
    assert circulo_maximo_magias_lancaveis_mb(slug, nivel) == esperado


def test_tipo_lista_magias():
    assert tipo_lista_magias_por_classe_mb("clerigo") == "divina"
    assert tipo_lista_magias_por_classe_mb("mago") == "arcana"
    assert tipo_lista_magias_por_classe_mb("guerreiro") is None
