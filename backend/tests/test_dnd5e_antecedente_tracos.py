"""Regras D&D 5E — traços de antecedente."""

import pytest

from app.games.dnd5e.rules.antecedente_tracos import (
    normalizar_tracos_escolhidos,
    validar_tracos_antecedente_na_ficha,
)
from app.games.dnd5e.rules.antecedentes import antecedente_do_catalogo, gerar_tracos
from app.games.dnd5e.rules.ficha import validar_ficha_para_gravacao


def test_gerar_tracos_reprodutivel():
    ant = antecedente_do_catalogo("acolito")
    assert ant is not None
    import random

    a = gerar_tracos(ant, rng=random.Random(7))
    b = gerar_tracos(ant, rng=random.Random(7))
    assert a.personalidade == b.personalidade


def test_validar_tracos_completos():
    opcoes = antecedente_do_catalogo("nobre")
    assert opcoes is not None
    tracos = {
        "personalidade": [opcoes.tracos_modelo.personalidade[0]],
        "ideais": [opcoes.tracos_modelo.ideais[0]],
        "lacos": [opcoes.tracos_modelo.lacos[0]],
        "fraquezas": [opcoes.tracos_modelo.fraquezas[0]],
    }
    out = normalizar_tracos_escolhidos(tracos, "nobre")
    assert all(len(out[k]) == 1 for k in out)


def test_validar_ficha_exige_tracos():
    base = {
        k: 10
        for k in (
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        )
    }
    ant = antecedente_do_catalogo("charlatao")
    ficha = {
        "raca_slug": "anao",
        "classe_slug": "guerreiro",
        "antecedente_slug": "charlatao",
        "scores_base": base,
        "pericias_classe_escolhidas": ["atletismo", "intimidacao"],
        "inventario": {"equipamentos": [], "ouro_po": 0},
    }
    with pytest.raises(ValueError, match="traço"):
        validar_ficha_para_gravacao(ficha, nivel=1)

    ficha["antecedente_tracos"] = {
        "personalidade": [ant.tracos_modelo.personalidade[0]],
        "ideais": [ant.tracos_modelo.ideais[0]],
        "lacos": [ant.tracos_modelo.lacos[0]],
        "fraquezas": [ant.tracos_modelo.fraquezas[0]],
    }
    out = validar_ficha_para_gravacao(ficha, nivel=1)
    assert out["antecedente_tracos"]["personalidade"]
