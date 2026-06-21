"""Ferramentas de proficiência nos antecedentes."""

from app.games.dnd5e.rules.antecedentes import antecedente_do_catalogo
from app.games.dnd5e.rules.catalogo_regras import listar_antecedentes_catalogo
from app.games.dnd5e.rules.ficha import montar_resumo_ficha


def test_catalogo_expoem_ferramentas():
    rows = {r["slug"]: r for r in listar_antecedentes_catalogo()}
    assert "Ferramentas de ladrão" in rows["criminoso"]["ferramentas"]
    assert rows["acolito"]["ferramentas"] == []


def test_antecedente_eremita_herbalismo():
    ant = antecedente_do_catalogo("eremita")
    assert ant is not None
    assert "Kit de herbalismo" in ant.ferramentas


def test_preview_ficha_inclui_ferramentas_antecedente():
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
    res = montar_resumo_ficha(
        raca_slug="humano",
        classe_slug="guerreiro",
        scores_base=base,
        antecedente_slug="criminoso",
        pericias_classe_escolhidas=["atletismo", "intimidacao"],
    )
    assert res["antecedente"]["ferramentas"]
