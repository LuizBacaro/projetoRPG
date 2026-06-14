"""Regras MB — magias preparadas (mago)."""

from app.games.tormenta.rules.magias_preparadas_t20 import (
    preview_preparadas_mb,
    teto_preparadas_mb,
    validar_adicionar_preparada_mb,
    validar_lancar_magia_preparador_mb,
)


def test_teto_mago_nivel_3_int_18():
    assert teto_preparadas_mb("mago", 3, int_valor=18) == 7


def test_preparar_exige_grimorio():
    ok, msg = validar_adicionar_preparada_mb(
        slug_classe="mago",
        nivel=3,
        magia_slug="alarme",
        circulo_magia=1,
        vinculos_existentes=[],
        int_valor=18,
    )
    assert ok is False
    assert "livro" in msg.lower()


def test_preparar_com_grimorio_ok():
    ok, _ = validar_adicionar_preparada_mb(
        slug_classe="mago",
        nivel=3,
        magia_slug="alarme",
        circulo_magia=1,
        vinculos_existentes=[
            {"papel": "grimorio", "magia_slug": "alarme", "circulo": 1}
        ],
        int_valor=18,
    )
    assert ok is True


def test_lancar_circulo_1_exige_preparada():
    ok, msg = validar_lancar_magia_preparador_mb(
        slug_classe="mago",
        magia_slug="alarme",
        circulo_magia=1,
        vinculos=[{"papel": "grimorio", "magia_slug": "alarme"}],
    )
    assert ok is False
    assert "preparadas" in msg.lower()


def test_lancar_truque_exige_grimorio():
    ok, msg = validar_lancar_magia_preparador_mb(
        slug_classe="mago",
        magia_slug="stub_truque_arc",
        circulo_magia=0,
        vinculos=[],
    )
    assert ok is False
    assert "truque" in msg.lower() or "livro" in msg.lower()


def test_preview_preparadas():
    p = preview_preparadas_mb(
        slug_classe="mago",
        nivel=3,
        vinculos=[{"papel": "preparada", "magia_slug": "a", "circulo": 1}],
        int_valor=18,
    )
    assert p["preparadas_usadas"] == 1
    assert p["preparadas_max"] == 7


def test_teto_clerigo_nivel_3_sab_14():
    assert teto_preparadas_mb("clerigo", 3, sab_valor=14) == 5


def test_clerigo_preparar_sem_grimorio_ok():
    vinculos = [
        {"papel": "conhecida", "magia_slug": "stub_1_circulo_div", "circulo": 1},
    ]
    ok, _ = validar_adicionar_preparada_mb(
        slug_classe="clerigo",
        nivel=3,
        magia_slug="stub_1_circulo_div",
        circulo_magia=1,
        vinculos_existentes=vinculos,
        sab_valor=14,
    )
    assert ok is True


def test_clerigo_preparar_arcana_rejeita():
    ok, msg = validar_adicionar_preparada_mb(
        slug_classe="clerigo",
        nivel=3,
        magia_slug="alarme",
        circulo_magia=1,
        vinculos_existentes=[],
        sab_valor=14,
    )
    assert ok is False
    assert "divina" in msg.lower() or "arcana" in msg.lower()


def test_clerigo_lancar_truque_divino_sem_vinculo():
    ok, _ = validar_lancar_magia_preparador_mb(
        slug_classe="clerigo",
        magia_slug="virtude",
        circulo_magia=0,
        vinculos=[],
        divindade_slug="lena",
    )
    assert ok is True


def test_clerigo_lancar_circulo_1_exige_preparada():
    ok, msg = validar_lancar_magia_preparador_mb(
        slug_classe="clerigo",
        magia_slug="stub_1_circulo_div",
        circulo_magia=1,
        vinculos=[],
    )
    assert ok is False
    assert "preparadas" in msg.lower()
