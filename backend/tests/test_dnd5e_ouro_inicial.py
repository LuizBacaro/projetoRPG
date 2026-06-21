"""Regras D&D 5E — ouro inicial por classe."""

import random

import pytest

from app.games.dnd5e.rules.antecedentes import antecedente_do_catalogo
from app.games.dnd5e.rules.ficha import validar_ficha_para_gravacao
from app.games.dnd5e.rules.ouro_inicial import (
    rolar_ouro_inicial_classe,
    sincronizar_ouro_classe_na_ficha,
)


def _tracos_sample(slug: str) -> dict:
    ant = antecedente_do_catalogo(slug)
    assert ant is not None and ant.tracos_modelo is not None
    m = ant.tracos_modelo
    return {
        "personalidade": [m.personalidade[0]],
        "ideais": [m.ideais[0]],
        "lacos": [m.lacos[0]],
        "fraquezas": [m.fraquezas[0]],
    }


def test_rolar_ouro_guerreiro_reprodutivel():
    a = rolar_ouro_inicial_classe("guerreiro", rng=random.Random(7))
    b = rolar_ouro_inicial_classe("guerreiro", rng=random.Random(7))
    assert a == b
    assert a["multiplicador"] == 10
    assert len(a["dados"]) == 5
    assert a["total"] == sum(a["dados"]) * 10


def test_rolar_ouro_monge_sem_multiplicador():
    roll = rolar_ouro_inicial_classe("monge", rng=random.Random(1))
    assert roll["multiplicador"] == 1
    assert roll["total"] == sum(roll["dados"])
    assert roll["formula"] == "5d4 gp"


def test_sincronizar_ouro_classe_na_ficha():
    ficha = {
        "classe_slug": "ladino",
        "inventario": {"equipamentos": [], "ouro_po": 0},
    }
    out = sincronizar_ouro_classe_na_ficha(ficha, rng=random.Random(3))
    assert out["classe_ouro_slug"] == "ladino"
    assert out["ouro_classe_aplicado"] > 0
    assert out["inventario"]["ouro_po"] == out["ouro_classe_aplicado"]


def test_sincronizar_troca_classe_substitui_ouro():
    ficha = sincronizar_ouro_classe_na_ficha(
        {"classe_slug": "mago", "inventario": {"ouro_po": 0}},
        rng=random.Random(1),
    )
    ouro_mago = ficha["ouro_classe_aplicado"]
    ficha["classe_slug"] = "barbaro"
    out = sincronizar_ouro_classe_na_ficha(ficha, rng=random.Random(2))
    assert out["classe_ouro_slug"] == "barbaro"
    assert out["ouro_classe_aplicado"] != ouro_mago
    assert out["inventario"]["ouro_po"] == out["ouro_classe_aplicado"]


def test_validar_ficha_soma_ouro_classe_e_antecedente():
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
    ficha = {
        "raca_slug": "elfo",
        "classe_slug": "ladino",
        "antecedente_slug": "nobre",
        "antecedente_idiomas": ["draconico"],
        "antecedente_tracos": _tracos_sample("nobre"),
        "scores_base": base,
        "pericias_classe_escolhidas": [
            "furtividade",
            "enganacao",
            "percepcao",
            "investigacao",
        ],
        "inventario": {"equipamentos": [], "ouro_po": 0},
    }
    out = validar_ficha_para_gravacao(ficha, nivel=1)
    assert out["ouro_classe_aplicado"] > 0
    assert out["antecedente_ouro_aplicado"] == 25
    assert out["antecedente_idiomas"] == ["draconico"]
    assert (
        out["inventario"]["ouro_po"]
        == out["ouro_classe_aplicado"] + out["antecedente_ouro_aplicado"]
    )
