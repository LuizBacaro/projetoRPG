"""Testes unitários — conjuração MB (PM, habilidade-chave, custo por círculo)."""

from __future__ import annotations

from app.games.tormenta.rules.conjuracao_t20 import (
    custo_pm_preparar_ou_lancar_magia,
    habilidade_chave_conjuracao,
    pontos_magia_maximos_conjuracao,
)


def _attrs(int_: int, sab: int, car: int, for_=10, des=10, con=10):
    return for_, des, con, int_, sab, car


def test_habilidade_chave_conjuracao():
    assert habilidade_chave_conjuracao("mago") == "int"
    assert habilidade_chave_conjuracao("bardo") == "car"
    assert habilidade_chave_conjuracao("clerigo") == "sab"
    assert habilidade_chave_conjuracao("barbaro") is None


def test_pm_mago_e_feiticeiro():
    f, d, c, i, s, ca = _attrs(18, 10, 16)
    assert pontos_magia_maximos_conjuracao("mago", 1, f, d, c, i, s, ca) == 5
    assert pontos_magia_maximos_conjuracao("mago", 2, f, d, c, i, s, ca) == 8
    assert pontos_magia_maximos_conjuracao("feiticeiro", 1, f, d, c, i, s, ca) == 6


def test_pm_bardo_e_clerigo():
    f, d, c, i, s, ca = _attrs(10, 14, 14)
    assert pontos_magia_maximos_conjuracao("bardo", 3, f, d, c, i, s, ca) == 7
    f, d, c, i, s, ca = _attrs(10, 14, 10)
    assert pontos_magia_maximos_conjuracao("clerigo", 2, f, d, c, i, s, ca) == 6


def test_pm_paladino_ranger_inicio_nivel_5():
    f, d, c, i, s, ca = _attrs(10, 14, 10)
    assert pontos_magia_maximos_conjuracao("ranger", 4, f, d, c, i, s, ca) is None
    assert pontos_magia_maximos_conjuracao("ranger", 5, f, d, c, i, s, ca) == 3
    assert pontos_magia_maximos_conjuracao("ranger", 6, f, d, c, i, s, ca) == 4
    assert pontos_magia_maximos_conjuracao("paladino", 5, f, d, c, i, s, ca) == 3


def test_custo_pm_circulo_mb():
    assert custo_pm_preparar_ou_lancar_magia(0) == 0
    assert custo_pm_preparar_ou_lancar_magia(1) == 1
    assert custo_pm_preparar_ou_lancar_magia(3) == 3
    assert custo_pm_preparar_ou_lancar_magia(-1) == 0


def test_custo_pm_circulo_v13():
    assert custo_pm_preparar_ou_lancar_magia(1, "v13") == 1
    assert custo_pm_preparar_ou_lancar_magia(2, "v13") == 3
    assert custo_pm_preparar_ou_lancar_magia(3, "v13") == 6
    assert custo_pm_preparar_ou_lancar_magia(4, "v13") == 10
    assert custo_pm_preparar_ou_lancar_magia(5, "v13") == 15


def test_cd_magia_v13():
    from app.games.tormenta.rules.conjuracao_t20 import cd_resistencia_magia_t20

    assert cd_resistencia_magia_t20(8, 5, "v13") == 19


def test_pm_arcanista_v13():
    f, d, c, i, s, ca = _attrs(4, 2, 3)
    assert (
        pontos_magia_maximos_conjuracao("arcanista", 5, f, d, c, i, s, ca, "v13") == 30
    )
