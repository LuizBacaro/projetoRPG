"""Domínio e API — montagem de ficha D&D 5e."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd5e.api.v1.regras import router as dnd5e_regras_router
from app.games.dnd5e.rules.ficha import (
    calcular_atributos_efetivos,
    hp_max_nivel_1,
    montar_resumo_ficha,
    validar_ficha_para_gravacao,
)
from app.shared.core.deps import get_usuario_atual


def test_elfo_dex_mais_2():
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
    eff = calcular_atributos_efetivos(base, "elfo")
    assert eff["dexterity"] == 16


def test_guerreiro_hp_nivel_1_con_mais_2():
    assert hp_max_nivel_1("guerreiro", 2) == 12  # d10 + 2


def test_meio_elfo_bonus_extra():
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
    eff = calcular_atributos_efetivos(
        base,
        "meio_elfo",
        bonus_habilidade_extra={"strength": 1, "wisdom": 1},
    )
    assert eff["charisma"] == 12
    assert eff["strength"] == 11
    assert eff["wisdom"] == 11


@pytest.fixture
def client_calc():
    app = FastAPI()
    app.include_router(dnd5e_regras_router, prefix="/api/v1")
    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")
    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_post_calcular_atributos(client_calc):
    r = client_calc.post(
        "/api/v1/dnd5e/regras/calcular-atributos",
        json={
            "raca_slug": "elfo",
            "classe_slug": "ladino",
            "scores_base": {
                "strength": 10,
                "dexterity": 15,
                "constitution": 12,
                "intelligence": 10,
                "wisdom": 10,
                "charisma": 8,
            },
        },
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["scores_efetivos"]["dexterity"] == 17
    assert body["hp_max_nivel_1"] == 9  # d8 + 1 CON
    assert body["ca_base"] == 13  # 10 + 3 DEX
    assert body["ca_total"] == 13
    assert len(body["pericias"]) == 18


def test_validar_ficha_exige_pericias_classe():
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
        "scores_base": base,
        "pericias_classe_escolhidas": ["furtividade"],
    }
    with pytest.raises(ValueError, match="exatamente 4"):
        validar_ficha_para_gravacao(ficha, nivel=1)


def test_validar_ficha_enriquece_ca():
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
    ficha = {
        "raca_slug": "elfo",
        "classe_slug": "ladino",
        "scores_base": base,
        "pericias_classe_escolhidas": [
            "furtividade",
            "enganacao",
            "percepcao",
            "investigacao",
        ],
        "armadura_slug": "couro-batido",
    }
    out = validar_ficha_para_gravacao(ficha, nivel=1)
    assert out["ca_total"] == 15  # 12 + 3 DEX
    assert "furtividade" in out["pericias_proficientes"]
