"""Regras MB — magias conhecidas (bardo, feiticeiro)."""

from __future__ import annotations

from app.games.tormenta.rules.magias_conhecidas_progressao_t20 import (
    bardo_pode_trocar_magia_mb,
    limite_magias_conhecidas_circulo_mb,
    preview_magias_conhecidas_mb,
    total_magias_conhecidas_max_mb,
    validar_adicionar_conhecida_mb,
)


def test_feiticeiro_nivel_1_limite_circulo_1():
    assert limite_magias_conhecidas_circulo_mb("feiticeiro", 1, 1) == 2
    assert total_magias_conhecidas_max_mb("feiticeiro", 1) == 6


def test_bardo_nivel_5_troca():
    assert bardo_pode_trocar_magia_mb(5) is True
    assert bardo_pode_trocar_magia_mb(4) is False


def test_validar_adicionar_conhecida_excede():
    ok, msg = validar_adicionar_conhecida_mb(
        slug_classe="feiticeiro",
        nivel=1,
        circulo_magia=1,
        vinculos_existentes=[
            {"papel": "conhecida", "circulo": 1},
            {"papel": "conhecida", "circulo": 1},
        ],
    )
    assert ok is False
    assert "limite" in msg.lower()


def test_preview_conhecidas_bardo():
    p = preview_magias_conhecidas_mb(
        slug_classe="bardo",
        nivel=5,
        vinculos=[{"magia_slug": "stub_truque_arc", "papel": "conhecida"}],
    )
    assert p["usa_limite_conhecidas"] is True
    assert p["bardo_pode_trocar"] is True
    assert p["total_conhecidas_max"] == 13
