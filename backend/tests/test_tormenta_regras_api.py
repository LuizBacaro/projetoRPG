"""Integração HTTP — regras Tormenta (payload estático para a ficha)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.tormenta.api.v1.regras import router as tormenta_regras_router
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario


@pytest.fixture(scope="function")
def client_regras_tormenta():
    app = FastAPI()
    app.include_router(tormenta_regras_router, prefix="/api/v1")

    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")

    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_regras_atributos(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/atributos")
    assert r.status_code == 200
    body = r.json()
    assert body["pontos_compra_iniciais"] == 20
    assert len(body["custos"]) == 11
    assert body["custos"][0]["valor"] == 8
    assert len(body["pericias"]) == 32
    assert body["pericias"][0]["nome"] == "Acrobacia"
    assert body["pericias"][0]["atributo"] == "des"
    assert body["pericias"][0]["somente_treinado"] is False
    assert body["pericias"][0]["penalidade_armadura"] is True
    assert body["pericias"][1]["nome"] == "Adestramento"
    assert body["pericias"][1]["somente_treinado"] is True
    assert body["pericias"][1]["penalidade_armadura"] is False
    assert body["pericias"][-1]["atributo"] is None
    assert body["pericias"][-1]["somente_treinado"] is False
    assert body["pericias"][-1]["penalidade_armadura"] is False


def test_get_regras_racas(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/racas")
    assert r.status_code == 200
    body = r.json()
    assert "racas" in body
    assert len(body["racas"]) >= 11
    assert "idiomas_geral_mb" in body and len(body["idiomas_geral_mb"]) > 50
    assert "idiomas_tabela_mb" in body and len(body["idiomas_tabela_mb"]) >= 10
    slugs = {x["slug"] for x in body["racas"]}
    assert "anao" in slugs and "humano" in slugs
    assert "gnomo" in slugs and "meio_elfo" in slugs and "meio_orc" in slugs
    anao = next(x for x in body["racas"] if x["slug"] == "anao")
    assert anao["ajustes"]["con"] == 4
    assert anao["ajustes"]["des"] == -2
    assert anao.get("idioma_racial_mb") == "Anão"
    hum = next(x for x in body["racas"] if x["slug"] == "humano")
    assert hum.get("idioma_racial_mb") is None


def test_get_regras_classes(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/classes")
    assert r.status_code == 200
    body = r.json()
    assert "classes" in body and "beneficios_por_nivel" in body
    assert len(body["classes"]) >= 10
    assert len(body["beneficios_por_nivel"]) == 20
    bar = next(x for x in body["classes"] if x["slug"] == "barbaro")
    assert bar["bba_tipo"] == "plein"
    assert bar["habilidades_por_nivel"]["1"]


def test_get_regras_equipamentos_pagina(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/equipamentos",
        params={"q": "espada", "skip": 0, "limit": 5},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert "itens" in body and "total" in body
    assert body["total"] >= 3
    assert len(body["itens"]) <= 5
    assert all("espada" in x["nome"].lower() for x in body["itens"])
    assert r.headers.get("X-Total-Count")


def test_get_regras_talentos_pagina(client_regras_tormenta):
    r = client_regras_tormenta.get(
        "/api/v1/tormenta/regras/talentos",
        params={"q": "usar", "skip": 0, "limit": 10},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] >= 1
    assert len(body["itens"]) >= 1
    assert any("usar" in x["nome"].lower() for x in body["itens"])


def test_get_regras_armaduras_protecao_pagina(client_regras_tormenta):
    r = client_regras_tormenta.get("/api/v1/tormenta/regras/armaduras-protecao", params={"skip": 0, "limit": 20})
    assert r.status_code == 200, r.text
    body = r.json()
    assert "itens" in body and "total" in body
    assert body["total"] == 0
    assert body["itens"] == []
