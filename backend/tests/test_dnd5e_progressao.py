"""Progressão D&D 5e — HP incremental, marcos feat/ASI, geração de atributos."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd5e.api.v1.personagens import router as dnd5e_personagens_router
from app.games.dnd5e.api.v1.regras import router as dnd5e_regras_router
from app.games.dnd5e.rules.progressao import (
    aplicar_marco_na_ficha,
    calcular_hp_max_total,
    gerar_scores_4d6,
    hp_max_nivel_1,
    matriz_padrao_scores,
    migrar_ficha_para_v2,
    montar_hp_resumo,
    registrar_hp_roll_na_ficha,
    validar_nivel_vs_experiencia,
)
from app.shared.core.deps import get_usuario_atual


def test_migrar_ficha_v1_para_v2():
    ficha = {"raca_slug": "humano", "classe_slug": "guerreiro"}
    out = migrar_ficha_para_v2(ficha)
    assert out["v"] == 2
    assert out["metodo_atributos"] == "padrao"
    assert "progressao" in out
    assert out["progressao"]["hp_rolls"] == []


def test_gerar_scores_4d6_reproduzivel():
    a = gerar_scores_4d6(seed=42)
    b = gerar_scores_4d6(seed=42)
    assert a == b
    assert len(a) == 6


def test_matriz_padrao():
    scores = matriz_padrao_scores()
    assert scores["strength"] == 15
    assert scores["charisma"] == 8


def test_hp_max_total_nivel_3():
    rolls = [
        {"nivel": 2, "roll": 6, "con_mod": 2, "ganho": 8},
        {"nivel": 3, "roll": 5, "con_mod": 2, "ganho": 7},
    ]
    total = calcular_hp_max_total("guerreiro", 2, 3, rolls)
    assert total == 12 + 8 + 7


def test_hp_nivel_1_com_roll_manual():
    rolls = [{"nivel": 1, "roll": 8, "con_mod": 2, "ganho": 10}]
    assert calcular_hp_max_total("guerreiro", 2, 1, rolls) == 10


def test_hp_nivel_1_anao_bonus_por_nivel():
    rolls = [{"nivel": 1, "roll": 8, "con_mod": 2, "ganho": 10}]
    assert calcular_hp_max_total("guerreiro", 2, 1, rolls, raca_slug="anao") == 11


def test_hp_tough_mais_raca_nivel_3():
    rolls = [
        {"nivel": 1, "roll": 10, "con_mod": 2, "ganho": 12},
        {"nivel": 2, "roll": 6, "con_mod": 2, "ganho": 8},
        {"nivel": 3, "roll": 5, "con_mod": 2, "ganho": 7},
    ]
    total = calcular_hp_max_total(
        "guerreiro", 2, 3, rolls, raca_slug="anao", feats=["tough"]
    )
    # nív.1: 12+3, nív.2: 8+3, nív.3: 7+3
    assert total == 15 + 11 + 10


def test_registrar_hp_roll_nivel_1():
    ficha = migrar_ficha_para_v2({"classe_slug": "mago", "raca_slug": "humano"})
    ficha, entrada = registrar_hp_roll_na_ficha(
        ficha, nivel=1, classe_slug="mago", con_mod=-1, roll=4
    )
    assert entrada["ganho"] == 3  # 4 + (-1), mín. 1 -> actually max(1, 4-1)=3
    resumo = montar_hp_resumo("mago", -1, 1, ficha["progressao"]["hp_rolls"])
    assert resumo["total"] == 3


def test_hp_max_nivel_1_maximo_dado():
    assert hp_max_nivel_1("guerreiro", 2) == 12


def test_validar_nivel_vs_xp():
    validar_nivel_vs_experiencia(5, 6500)
    with pytest.raises(ValueError, match="Nível 5"):
        validar_nivel_vs_experiencia(5, 900)


def test_registrar_hp_roll_e_marco_feat():
    ficha = migrar_ficha_para_v2(
        {
            "raca_slug": "humano",
            "classe_slug": "guerreiro",
            "scores_base": matriz_padrao_scores(),
        }
    )
    ficha, entrada = registrar_hp_roll_na_ficha(
        ficha,
        nivel=2,
        classe_slug="guerreiro",
        con_mod=2,
        roll=7,
    )
    assert entrada["ganho"] == 9
    ficha = aplicar_marco_na_ficha(
        ficha,
        {"nivel": 4, "tipo": "feat", "slug": "alert"},
    )
    assert "alert" in ficha["feats"]


@pytest.fixture
def client_regras():
    app = FastAPI()
    app.include_router(dnd5e_regras_router, prefix="/api/v1")
    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")
    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_post_gerar_atributos_padrao(client_regras):
    r = client_regras.post(
        "/api/v1/dnd5e/regras/gerar-atributos",
        json={"metodo": "padrao"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["metodo"] == "padrao"
    assert data["scores_base"]["strength"] == 15


def test_post_gerar_atributos_4d6(client_regras):
    r = client_regras.post(
        "/api/v1/dnd5e/regras/gerar-atributos",
        json={"metodo": "4d6", "seed": 99},
    )
    assert r.status_code == 200
    assert r.json()["metodo"] == "4d6"
