"""PM multiclasse v1.3 e dinheiro inicial Tabela 3-1."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.dinheiro_inicial_v13_t20 import (
    dinheiro_por_nivel,
    preview_dinheiro_inicial_v13,
)
from app.games.tormenta.rules.progressao_pv_t20 import (
    pm_maximos_v13_multiclasse,
    preview_pm_multiclasse_v13,
)


def test_pm_multiclasse_v13_exemplo_livro() -> None:
    prev = preview_pm_multiclasse_v13(
        [{"slug": "arcanista", "nivel": 3}, {"slug": "paladino", "nivel": 1}]
    )
    assert prev["pm_max"] == 21
    assert "Arcanista" in prev["formula"]
    assert pm_maximos_v13_multiclasse({"arcanista": 3, "paladino": 1}) == 21


def test_pm_multiclasse_v13_agrega_mesma_classe() -> None:
    prev = preview_pm_multiclasse_v13(
        [{"slug": "barbaro", "nivel": 2}, {"slug": "barbaro", "nivel": 1}]
    )
    assert prev["pm_max"] == 9  # 3×3
    assert len(prev["breakdown"]) == 1
    assert prev["breakdown"][0]["nivel"] == 3


def test_dinheiro_nivel_1_e_4d6() -> None:
    d = dinheiro_por_nivel(1)
    assert d["tipo"] == "4d6"
    assert d["valor"] is None


@pytest.mark.parametrize(
    "nivel,esperado",
    [
        (2, 300),
        (5, 2000),
        (10, 13000),
        (20, 260000),
    ],
)
def test_dinheiro_tabela_3_1(nivel: int, esperado: int) -> None:
    d = dinheiro_por_nivel(nivel)
    assert d["tipo"] == "fixo"
    assert d["valor"] == esperado


def test_preview_dinheiro_inicial_v13() -> None:
    prev = preview_dinheiro_inicial_v13(7)
    assert prev["regra_versao"] == "v13"
    assert prev["valor"] == 5000
