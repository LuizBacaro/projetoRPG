"""Regras de elegibilidade ao grimório MB (nível efetivo / override)."""

from __future__ import annotations

from app.games.tormenta.rules.grimorio_elegibilidade_t20 import (
    nivel_efetivo_conjuracao_mb,
    resumo_elegibilidade_grimorio_mb,
)


def test_nivel_efetivo_override():
    assert nivel_efetivo_conjuracao_mb({"tormenta_nivel_conjurador_mb": 5}, 1) == 5
    assert nivel_efetivo_conjuracao_mb({"tormenta_nivel_conjurador_mb": "12"}, 3) == 12


def test_nivel_efetivo_soma_classes_conjuradoras():
    fj = {
        "tormenta_niveis_classe_mb": [
            {"slug": "mago", "nivel": 2},
            {"slug": "guerreiro", "nivel": 4},
        ]
    }
    assert nivel_efetivo_conjuracao_mb(fj, 10) == 2


def test_paladino_nivel_personagem_baixo_override_libera():
    ok, msg = resumo_elegibilidade_grimorio_mb(
        tipo="jogador",
        nivel=4,
        ficha_json={
            "tormenta_classe_mb_slug": "paladino",
            "tormenta_nivel_conjurador_mb": 5,
        },
    )
    assert ok is True
    assert msg == ""


def test_paladino_nivel_4_sem_override_bloqueia():
    ok, msg = resumo_elegibilidade_grimorio_mb(
        tipo="jogador",
        nivel=4,
        ficha_json={"tormenta_classe_mb_slug": "paladino"},
    )
    assert ok is False
    assert "5" in msg
