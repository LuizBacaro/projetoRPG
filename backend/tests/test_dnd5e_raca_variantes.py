"""Variantes raciais draconato/tiefling."""

import pytest

from app.games.dnd5e.rules.ficha import montar_resumo_ficha
from app.games.dnd5e.rules.raca_traits import reduzir_dano_racial
from app.games.dnd5e.rules.raca_variantes import (
    listar_variantes_raca,
    tipo_dano_resistencia_racial,
    validar_variante_racial,
    variante_por_slug,
)


def test_draconato_oito_variantes():
    vars_ = listar_variantes_raca("draconato")
    assert len(vars_) == 8
    assert variante_por_slug("draconato", "red")["tipo_dano"] == "fogo"


def test_tiefling_quatro_variantes():
    assert len(listar_variantes_raca("tiefling")) == 4


def test_resistencia_draconato_red():
    assert tipo_dano_resistencia_racial("draconato", "red") == "fogo"
    dano, msg = reduzir_dano_racial("draconato", 10, "fogo", raca_variante_slug="red")
    assert dano == 5
    assert "Resistência racial" in msg


def test_resistencia_tiefling_levistus():
    dano, _ = reduzir_dano_racial("tiefling", 8, "frio", raca_variante_slug="levistus")
    assert dano == 4


def test_preview_ficha_com_variante():
    res = montar_resumo_ficha(
        raca_slug="draconato",
        raca_variante_slug="green",
        classe_slug="guerreiro",
        scores_base={
            k: 10
            for k in (
                "strength",
                "dexterity",
                "constitution",
                "intelligence",
                "wisdom",
                "charisma",
            )
        },
        pericias_classe_escolhidas=["atletismo", "intimidacao"],
    )
    assert res["raca_variante"]["slug"] == "green"
    assert "Verde" in res["tracos_resumo"]
    assert "veneno" in res["tracos_resumo"].lower() or "Veneno" in res["tracos_resumo"]


def test_variante_obrigatoria_draconato():
    with pytest.raises(ValueError, match="linhagem"):
        validar_variante_racial("draconato", None)


def test_gravacao_exige_variante_draconato():
    from app.games.dnd5e.rules.ficha import validar_ficha_para_gravacao

    with pytest.raises(ValueError, match="linhagem"):
        validar_ficha_para_gravacao(
            {
                "raca_slug": "draconato",
                "classe_slug": "guerreiro",
                "scores_base": {
                    k: 10
                    for k in (
                        "strength",
                        "dexterity",
                        "constitution",
                        "intelligence",
                        "wisdom",
                        "charisma",
                    )
                },
                "pericias_classe_escolhidas": ["atletismo", "intimidacao"],
            }
        )
