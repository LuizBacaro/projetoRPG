"""Perícias e proficiências D&D 5e."""

from __future__ import annotations

import pytest

from app.games.dnd5e.rules.ficha import montar_resumo_ficha
from app.games.dnd5e.rules.pericias import (
    montar_proficiencias_pericias,
    normalizar_pericia_slug,
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
