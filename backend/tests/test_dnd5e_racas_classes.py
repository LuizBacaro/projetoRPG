"""Domínio — raças e classes D&D 5e."""

from app.games.dnd5e.rules.classes import (
    CLASSE_SLUGS_VALIDOS,
    nivel_por_xp,
    xp_minima_por_nivel,
)
from app.games.dnd5e.rules.racas import RACA_SLUGS_VALIDOS, raca_por_slug


def test_nove_racas_validas():
    assert len(RACA_SLUGS_VALIDOS) == 9
    elfo = raca_por_slug("elfo")
    assert elfo is not None
    assert elfo["bonus_habilidades"]["dexterity"] == 2


def test_doze_classes_e_xp():
    assert len(CLASSE_SLUGS_VALIDOS) == 12
    assert nivel_por_xp(0) == 1
    assert nivel_por_xp(300) == 2
    assert nivel_por_xp(355000) == 20
    assert xp_minima_por_nivel(5) == 6500
    assert xp_minima_por_nivel(12) == 100000
