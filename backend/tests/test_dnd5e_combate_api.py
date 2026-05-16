"""API de combate D&D 5e."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd5e.api.v1.combate import router as dnd5e_combate_router
from app.shared.core.deps import get_usuario_atual


@pytest.fixture
def client_combate():
    app = FastAPI()
    app.include_router(dnd5e_combate_router, prefix="/api/v1")
    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")
    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_post_iniciativa(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/iniciativa",
        json={
            "combatentes": [
                {"id": "1", "nome": "A", "dex_mod": 2},
                {"id": "2", "nome": "B", "dex_mod": 0},
            ]
        },
    )
    assert r.status_code == 200, r.text
    ordem = r.json()["ordem"]
    assert len(ordem) == 2
    assert ordem[0]["iniciativa"] >= ordem[1]["iniciativa"]


def test_post_ataque(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/ataque",
        json={
            "mod_atributo": 3,
            "bonus_proficiencia": 2,
            "ac_alvo": 15,
            "rolagem_d20": 12,
        },
    )
    assert r.status_code == 200
    assert r.json()["acerto"] is True


def test_post_ataque_com_condicoes_alvo(client_combate):
    r = client_combate.post(
        "/api/v1/dnd5e/combate/ataque",
        json={
            "mod_atributo": 0,
            "bonus_proficiencia": 2,
            "ac_alvo": 25,
            "rolagem_d20": 5,
            "condicoes_alvo": ["incapacitado"],
            "corpo_a_corpo": True,
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["acerto"] is True
    assert body["acerto_automatico"] is True
