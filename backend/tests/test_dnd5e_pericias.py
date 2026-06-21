"""Perícias e proficiências D&D 5e."""

from __future__ import annotations

import pytest

from app.games.dnd5e.rules.ficha import montar_resumo_ficha
from app.games.dnd5e.rules.pericias import (
    aplicar_pericias_override,
    montar_proficiencias_automaticas,
    montar_proficiencias_pericias,
    normalizar_pericia_slug,
    validar_pericias_override,
    validar_skilled_pericias,
)


def test_normalizar_pericia_en():
    assert normalizar_pericia_slug("Stealth") == "furtividade"
    assert normalizar_pericia_slug("acrobacia") == "acrobacia"


def test_ladino_quatro_pericias():
    prof = montar_proficiencias_pericias(
        classe_slug="ladino",
        raca_slug="elfo",
        pericias_classe_escolhidas=[
            "furtividade",
            "enganacao",
            "percepcao",
            "investigacao",
        ],
    )
    assert len(prof) == 4


def test_antecedente_soldado_mais_classe():
    prof = montar_proficiencias_pericias(
        classe_slug="guerreiro",
        raca_slug="humano",
        antecedente_slug="soldado",
        pericias_classe_escolhidas=["intuicao", "historia"],
        pericia_racial_extra="percepcao",
    )
    assert "atletismo" in prof
    assert "intimidacao" in prof
    assert "intuicao" in prof
    assert "percepcao" in prof


def test_ca_com_armadura_e_escudo():
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
    base["dexterity"] = 14
    resumo = montar_resumo_ficha(
        raca_slug="humano",
        classe_slug="guerreiro",
        scores_base=base,
        armadura_slug="cota-malha",
        escudo_slug="escudo",
        pericias_classe_escolhidas=["atletismo", "intuicao"],
    )
    assert resumo["ca_base"] == 12  # 10 + 2 DEX
    assert resumo["ca_total"] == 18  # 14 + min(2,2) + 2 escudo


def test_escolha_classe_invalida():
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
    with pytest.raises(ValueError, match="não é opção válida"):
        montar_resumo_ficha(
            raca_slug="elfo",
            classe_slug="guerreiro",
            scores_base=base,
            pericias_classe_escolhidas=["arcanismo", "atletismo"],
        )


def test_pericias_override_adiciona_e_remove():
    auto = ["atletismo", "intuicao"]
    merged = aplicar_pericias_override(auto, {"furtividade": True, "atletismo": False})
    assert "furtividade" in merged
    assert "intuicao" in merged
    assert "atletismo" not in merged


def test_validar_pericias_override_rejeita_slug_invalido():
    with pytest.raises(ValueError, match="Perícia inválida"):
        validar_pericias_override({"foo_bar": True})


def test_resumo_pericias_override():
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
    resumo = montar_resumo_ficha(
        raca_slug="humano",
        classe_slug="guerreiro",
        scores_base=base,
        pericias_classe_escolhidas=["atletismo", "intuicao"],
        pericias_override={"furtividade": True, "atletismo": False},
    )
    slugs = {p["slug"] for p in resumo["pericias"] if p.get("proficiente")}
    assert "furtividade" in slugs
    assert "intuicao" in slugs
    assert "atletismo" not in slugs
    assert set(resumo["pericias_automaticas"]) == {"atletismo", "intuicao"}


def test_skilled_feat_adiciona_tres_proficiencias():
    prof = montar_proficiencias_automaticas(
        classe_slug="guerreiro",
        raca_slug="humano",
        pericias_classe_escolhidas=["atletismo", "intuicao"],
        feats=["skilled"],
        feat_escolhas={
            "skilled_pericias": ["furtividade", "percepcao", "investigacao"],
        },
    )
    assert "furtividade" in prof
    assert "percepcao" in prof
    assert "investigacao" in prof
    assert "atletismo" in prof


def test_validar_skilled_exige_tres_distintas():
    with pytest.raises(ValueError, match="3 perícias"):
        validar_skilled_pericias(["atletismo", "intuicao"])
    with pytest.raises(ValueError, match="3 perícias"):
        validar_skilled_pericias(["atletismo", "atletismo", "intuicao"])


def test_expertise_ladino_dobra_bonus():
    from app.games.dnd5e.rules.pericias import calcular_slots_expertise_classe

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
    base["dexterity"] = 14
    resumo = montar_resumo_ficha(
        raca_slug="humano",
        classe_slug="ladino",
        scores_base=base,
        pericias_classe_escolhidas=[
            "furtividade",
            "enganacao",
            "percepcao",
            "investigacao",
        ],
        expertise_pericias=["furtividade", "enganacao"],
        nivel=1,
    )
    assert calcular_slots_expertise_classe("ladino", 1) == 2
    furt = next(p for p in resumo["pericias"] if p["slug"] == "furtividade")
    perc = next(p for p in resumo["pericias"] if p["slug"] == "percepcao")
    assert furt["expertise"] is True
    assert furt["bonus"] == 6  # DEX +2 + prof 2×2
    assert perc["expertise"] is False
    assert perc["bonus"] == 2  # SAB +0 + prof +2


def test_bardo_expertise_nivel_3():
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
    base["charisma"] = 14
    resumo = montar_resumo_ficha(
        raca_slug="humano",
        classe_slug="bardo",
        scores_base=base,
        pericias_classe_escolhidas=["atuacao", "persuasao", "enganacao"],
        antecedente_slug="artesao-guilda",
        expertise_pericias=["atuacao", "persuasao"],
        nivel=3,
    )
    atu = next(p for p in resumo["pericias"] if p["slug"] == "atuacao")
    assert atu["expertise"] is True
    assert atu["bonus"] == 6  # CAR +2 + prof 2×2 at level 3


def test_skill_expert_feat_proficiencia_e_expertise():
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
    resumo = montar_resumo_ficha(
        raca_slug="humano",
        classe_slug="guerreiro",
        scores_base=base,
        pericias_classe_escolhidas=["atletismo", "intuicao"],
        feats=["skill-expert"],
        feat_escolhas={
            "skill_expert_nova": "historia",
            "skill_expert_expertise": "atletismo",
        },
        nivel=4,
    )
    slugs = set(resumo["pericias_proficientes"])
    assert "historia" in slugs
    atl = next(p for p in resumo["pericias"] if p["slug"] == "atletismo")
    assert atl["expertise"] is True
    assert atl["bonus"] == 4  # FOR +0 + prof 2×2 at level 4
