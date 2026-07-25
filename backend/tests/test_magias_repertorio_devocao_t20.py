"""Regras MB — repertório aprendido e devoção divindade (RF-T44d)."""

from app.games.tormenta.rules.devocao_divindade_t20 import (
    magia_e_truque_devocao_mb,
    truque_devocao_por_divindade_mb,
)
from app.games.tormenta.rules.magias_preparadas_t20 import (
    validar_adicionar_preparada_mb,
    validar_lancar_magia_preparador_mb,
)
from app.games.tormenta.rules.magias_repertorio_aprendido_t20 import (
    orcamento_repertorio_mb,
    preview_repertorio_mb,
    validar_adicionar_repertorio_mb,
)


def test_orcamento_clerigo_nivel_3_sab_14():
    # 3 (inicial + mod SAB) + 2×(nível−1) magias de 1º+ no repertório
    assert orcamento_repertorio_mb("clerigo", 3, sab_valor=14) == 9


def test_clerigo_preparar_exige_repertorio():
    ok, msg = validar_adicionar_preparada_mb(
        slug_classe="clerigo",
        nivel=3,
        magia_slug="stub_1_circulo_div",
        circulo_magia=1,
        vinculos_existentes=[],
        sab_valor=14,
    )
    assert ok is False
    assert "repertório" in msg.lower()


def test_clerigo_preparar_com_repertorio_ok():
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


def test_clerigo_lancar_truque_repertorio():
    ok, _ = validar_lancar_magia_preparador_mb(
        slug_classe="clerigo",
        magia_slug="brilho_div",
        circulo_magia=0,
        vinculos=[{"papel": "conhecida", "magia_slug": "brilho_div"}],
    )
    assert ok is True


def test_clerigo_lancar_truque_devocao_sem_repertorio():
    ok, _ = validar_lancar_magia_preparador_mb(
        slug_classe="clerigo",
        magia_slug="curar_ferimentos",
        circulo_magia=1,
        vinculos=[],
        divindade_slug="lena",
    )
    assert ok is True
    assert truque_devocao_por_divindade_mb("lena") == "curar_ferimentos"
    assert magia_e_truque_devocao_mb("lena", "curar_ferimentos")


def test_clerigo_lancar_truque_sem_vinculo_rejeita():
    ok, msg = validar_lancar_magia_preparador_mb(
        slug_classe="clerigo",
        magia_slug="brilho_div",
        circulo_magia=0,
        vinculos=[],
    )
    assert ok is False
    assert "repertório" in msg.lower() or "devoção" in msg.lower()


def test_preview_repertorio_clerigo():
    p = preview_repertorio_mb(
        slug_classe="clerigo",
        nivel=3,
        vinculos=[
            {"papel": "conhecida", "magia_slug": "stub_1_circulo_div", "circulo": 1}
        ],
        sab_valor=14,
    )
    assert p["repertorio_usadas"] == 1
    assert p["repertorio_max"] == 9
