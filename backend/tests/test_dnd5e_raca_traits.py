"""Traits raciais D&D 5e em combate."""

from app.games.dnd5e.rules.raca_traits import (
    aplicar_sorte_halfling,
    bonus_salvamento_racial,
    reduzir_dano_racial,
    resolver_ataque_com_raca,
    resolver_salvamento_racial,
    vantagem_salvamento_racial,
)


def test_elfo_vantagem_salvamento_encantamento():
    assert vantagem_salvamento_racial("elfo", categoria="encantamento") is True
    assert vantagem_salvamento_racial("elfo", condicoes=["enfeiticado"]) is True
    assert vantagem_salvamento_racial("humano", categoria="encantamento") is False


def test_anao_bonus_e_resistencia_veneno():
    assert bonus_salvamento_racial("anao", categoria="veneno") == 2
    dano, msg = reduzir_dano_racial("anao", 10, "veneno")
    assert dano == 5
    assert "Resistência anã" in msg
    assert reduzir_dano_racial("humano", 10, "veneno")[0] == 10


def test_halfling_sorte_rerrola_um():
    roll, reroll = aplicar_sorte_halfling(1, raca_slug="halfling", rng=lambda a, b: 15)
    assert roll == 15
    assert reroll == 15
    assert aplicar_sorte_halfling(1, raca_slug="humano")[0] == 1


def test_salvamento_elfo_vantagem_usa_maior_d20():
    rolls = iter([3, 18])

    def rng(a, b):
        return next(rolls)

    r = resolver_salvamento_racial(
        2,
        2,
        15,
        raca_slug="elfo",
        categoria="encantamento",
        rng=rng,
    )
    assert r["vantagem"] is True
    assert r["rolagem"] == 18
    assert r["total"] >= 15
    assert r["sucesso"] is True


def test_salvamento_anao_bonus_veneno():
    r = resolver_salvamento_racial(
        0,
        2,
        12,
        proficiente=True,
        raca_slug="anao",
        categoria="veneno",
        rolagem_d20=8,
    )
    assert r["bonus_racial"] == 2
    assert r["total"] == 12
    assert r["sucesso"] is True


def test_ataque_halfling_sorte():
    rolls = iter([1, 14])

    def rng(a, b):
        return next(rolls)

    r = resolver_ataque_com_raca(
        3,
        2,
        15,
        raca_slug="halfling",
        rng=rng,
    )
    assert r["sorte_reroll"] == 14
    assert r["rolagem"] == 14
    assert r["acerto"] is True
