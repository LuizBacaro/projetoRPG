"""Regras D&D 5E — magia."""

from app.games.dnd5e.rules.magia import (
    Conjurador,
    Magia,
    calcular_dc_magia,
    lancar_magia,
    recuperar_espacos_repouso_longo,
    salvaguarda_atinge_dc,
)


def test_dc_calcula() -> None:
    assert calcular_dc_magia(3, 4) == 15


def test_espacos_recuperam_repouso_longo() -> None:
    c = Conjurador(
        conjurador_id="m1",
        nome="Mago",
        classe="mago",
        nivel=5,
        mod_habilidade=4,
        bonus_proficiencia=3,
    )
    magia = Magia("bola-fogo", "Bola de Fogo", nivel=3)
    assert lancar_magia(c, magia) is True
    assert c.espacos_disponiveis(3) == 1
    recuperar_espacos_repouso_longo(c)
    assert c.espacos_disponiveis(3) == 2


def test_salvaguarda_atinge_dc() -> None:
    assert salvaguarda_atinge_dc(2, 15, rolagem_d20=14) is True
    assert salvaguarda_atinge_dc(2, 15, rolagem_d20=10) is False
