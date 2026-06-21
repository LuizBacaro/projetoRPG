"""Regras D&D 5E — idiomas de antecedente."""

import pytest

from app.games.dnd5e.rules.antecedentes import antecedente_do_catalogo
from app.games.dnd5e.rules.ficha import validar_ficha_para_gravacao
from app.games.dnd5e.rules.idiomas import (
    lista_idiomas_catalogo,
    normalizar_idiomas_escolhidos,
    validar_idiomas_antecedente,
    validar_idiomas_antecedente_na_ficha,
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


def test_lista_idiomas_catalogo_tem_comum_e_exoticos():
    rows = lista_idiomas_catalogo()
    slugs = {row["slug"] for row in rows}
    assert "comum" in slugs
    assert "draconico" in slugs
    assert len(rows) >= 15


def test_normalizar_remove_placeholder_e_duplicatas():
    out = normalizar_idiomas_escolhidos(
        ["elfico", "idioma_extra_1", "elfico", "invalido", "draconico"]
    )
    assert out == ["elfico", "draconico"]


def test_validar_idiomas_antecedente_exige_quantidade():
    with pytest.raises(ValueError, match="exatamente 2"):
        validar_idiomas_antecedente(["elfico"], qtd_esperada=2)
    out = validar_idiomas_antecedente(["elfico", "draconico"], qtd_esperada=2)
    assert out == ["elfico", "draconico"]


def test_validar_ficha_persiste_idiomas_antecedente():
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
        "antecedente_idiomas": ["elfico"],
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
    assert out["antecedente_idiomas"] == ["elfico"]


def test_validar_ficha_rejeita_idiomas_a_mais():
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
        "antecedente_slug": "acolito",
        "antecedente_idiomas": ["elfico", "draconico"],
        "antecedente_tracos": _tracos_sample("acolito"),
        "scores_base": base,
        "pericias_classe_escolhidas": [
            "furtividade",
            "enganacao",
            "percepcao",
            "investigacao",
        ],
        "inventario": {"equipamentos": [], "ouro_po": 0},
    }
    with pytest.raises(ValueError, match="exatamente 1"):
        validar_ficha_para_gravacao(ficha, nivel=1)


def test_validar_idiomas_sem_antecedente():
    assert validar_idiomas_antecedente_na_ficha({}) == []
