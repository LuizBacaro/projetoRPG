"""Proficiência em armas — Tormenta 20 v1.3 (RF-T05-v13c)."""

from __future__ import annotations

from app.games.tormenta.rules.proficiencia_arma_t20 import (
    PENALIDADE_ARMA_NAO_PROFICIENTE,
    ajustar_bonus_ataque_v13,
    penalidade_ataque_arma,
    proficiencia_arma_por_nome,
    proficiente_em_arma,
)


def test_arcanista_nao_proficiente_espada_longa() -> None:
    assert proficiencia_arma_por_nome("Espada longa") == "marcial"
    assert proficiente_em_arma("arcanista", "marcial") is False
    assert (
        penalidade_ataque_arma("arcanista", nome_arma="Espada longa")
        == PENALIDADE_ARMA_NAO_PROFICIENTE
    )


def test_guerreiro_proficiente_espada_longa() -> None:
    assert penalidade_ataque_arma("guerreiro", nome_arma="Espada longa") == 0


def test_clava_simples_arcanista_sem_penalidade() -> None:
    assert penalidade_ataque_arma("arcanista", nome_arma="Clava") == 0


def test_ajustar_bonus_arcanista_machado_batalha() -> None:
    data = ajustar_bonus_ataque_v13(8, "arcanista", nome_arma="Machado de batalha")
    assert data["bonus_base"] == 8
    assert data["bonus_efetivo"] == 3
    assert data["penalidade_nao_proficiente"] == 5
    assert data["proficiente"] is False
