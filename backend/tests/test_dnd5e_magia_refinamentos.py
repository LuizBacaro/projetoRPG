"""Refinamentos E4 — save metade, upcast de dano."""

from app.games.dnd5e.rules.magia import (
    escalar_dano_upcast,
    save_causa_metade_dano,
)


def test_save_causa_metade_dano_padrao() -> None:
    assert save_causa_metade_dano(dano="8d6", save_tipo="dex") is True
    assert save_causa_metade_dano(dano="8d6", save_tipo="nenhum") is False
    assert save_causa_metade_dano(dano=None, save_tipo="dex") is False


def test_save_sem_metade_em_disintegrate() -> None:
    assert (
        save_causa_metade_dano(
            dano="10d6+40",
            save_tipo="dex",
            slug="disintegrate",
        )
        is False
    )


def test_escalar_dano_upcast_fireball() -> None:
    expr = escalar_dano_upcast(
        "8d6",
        3,
        5,
        descricao_nivel_superior="+1d6 por nível acima do 3º",
    )
    assert expr == "10d6"


def test_escalar_dano_upcast_sem_delta() -> None:
    assert (
        escalar_dano_upcast("8d6", 3, 3, descricao_nivel_superior="+1d6/nível")
        == "8d6"
    )
