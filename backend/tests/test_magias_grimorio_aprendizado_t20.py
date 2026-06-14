"""Regras MB — orçamento de magias no livro (mago)."""

from app.games.tormenta.rules.magias_grimorio_aprendizado_t20 import (
    orcamento_magias_grimorio_mb,
    preview_grimorio_mb,
    validar_adicionar_grimorio_mb,
)


def test_orcamento_mago_nivel_1_int_18():
    # 3 + mod INT (+4) = 7
    assert orcamento_magias_grimorio_mb("mago", 1, int_valor=18) == 7


def test_orcamento_mago_nivel_3_int_18():
    # 7 + 2*(3-1) = 11
    assert orcamento_magias_grimorio_mb("mago", 3, int_valor=18) == 11


def test_truque_nao_consome_orcamento():
    ok, _ = validar_adicionar_grimorio_mb(
        slug_classe="mago",
        nivel=1,
        circulo_magia=0,
        tipo_magia="arcana",
        vinculos_existentes=[{"papel": "grimorio", "magia_slug": "a", "circulo": 0}]
        * 20,
        int_valor=8,
    )
    assert ok is True


def test_grimorio_excede_orcamento():
    vinculos = [
        {"papel": "grimorio", "magia_slug": f"m{i}", "circulo": 1} for i in range(7)
    ]
    ok, msg = validar_adicionar_grimorio_mb(
        slug_classe="mago",
        nivel=1,
        circulo_magia=1,
        tipo_magia="arcana",
        vinculos_existentes=vinculos,
        int_valor=18,
    )
    assert ok is False
    assert "Limite de magias no livro" in msg


def test_preview_grimorio_mago():
    p = preview_grimorio_mb(
        slug_classe="mago",
        nivel=1,
        vinculos=[{"papel": "grimorio", "magia_slug": "x", "circulo": 1}],
        int_valor=18,
    )
    assert p["usa_limite_grimorio"] is True
    assert p["grimorio_usadas"] == 1
    assert p["grimorio_max"] == 7
