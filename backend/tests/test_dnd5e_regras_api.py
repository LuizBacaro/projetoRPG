"""Integração HTTP — regras D&D 5e (payload estático para a ficha)."""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.games.dnd5e.api.v1.regras import router as dnd5e_regras_router
from app.shared.constants import GAME_SLUG_DND5E
from app.shared.core.config import settings
from app.shared.core.deps import get_usuario_atual, requer_game_dnd5e
from app.shared.models.usuario import Usuario


@pytest.fixture(scope="function")
def client_regras_dnd5e():
    app = FastAPI()
    app.include_router(dnd5e_regras_router, prefix="/api/v1")

    u = SimpleNamespace(id=1, perfil="jogador", email="t@example.com", nome="Teste")

    app.dependency_overrides[get_usuario_atual] = lambda: u
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_get_regras_racas(client_regras_dnd5e):
    r = client_regras_dnd5e.get("/api/v1/dnd5e/regras/racas")
    assert r.status_code == 200
    body = r.json()
    assert len(body["racas"]) == 9
    slugs = {x["slug"] for x in body["racas"]}
    assert slugs == {
        "anao",
        "elfo",
        "halfling",
        "humano",
        "draconato",
        "gnomo",
        "meio_elfo",
        "meio_orc",
        "tiefling",
    }
    elfo = next(x for x in body["racas"] if x["slug"] == "elfo")
    assert elfo["bonus_habilidades"]["dexterity"] == 2
    assert elfo["velocidade_metros"] == 9


def test_get_regras_classes(client_regras_dnd5e):
    r = client_regras_dnd5e.get("/api/v1/dnd5e/regras/classes")
    assert r.status_code == 200
    body = r.json()
    assert len(body["classes"]) == 12
    assert len(body["xp_por_nivel"]) == 20
    assert body["niveis_ganho_feat"] == [4, 8, 12, 16, 19]
    mago = next(x for x in body["classes"] if x["slug"] == "mago")
    assert mago["dado_vida"] == "d6"
    assert mago["habilidade_primaria_chave"] == "intelligence"


def test_get_regras_combate(client_regras_dnd5e):
    r = client_regras_dnd5e.get("/api/v1/dnd5e/regras/combate")
    assert r.status_code == 200
    body = r.json()
    assert body["critico_em"] == 20
    assert len(body["condicoes"]) >= 7
    assert "acao" in body["acoes_turno"]


def test_get_regras_magias(client_regras_dnd5e):
    r = client_regras_dnd5e.get(
        "/api/v1/dnd5e/regras/magias", params={"nivel": 1, "q": "misseis"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert (
        "conjuracao" in body and "habilidade_primaria_por_classe" in body["conjuracao"]
    )
    assert r.headers.get("X-Total-Count") == str(body["total"])


def test_get_regras_talentos(client_regras_dnd5e):
    r = client_regras_dnd5e.get(
        "/api/v1/dnd5e/regras/talentos", params={"tipo_bonus": "Combate"}
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    assert all(t["tipo_bonus"] == "Combate" for t in body["talentos"])


def test_get_regras_equipamento(client_regras_dnd5e):
    r = client_regras_dnd5e.get("/api/v1/dnd5e/regras/equipamento")
    assert r.status_code == 200
    body = r.json()
    assert len(body["armas_simples"]) >= 1
    assert len(body["armaduras"]) >= 1


def test_get_regras_antecedentes(client_regras_dnd5e):
    r = client_regras_dnd5e.get("/api/v1/dnd5e/regras/antecedentes")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 10
    assert r.headers.get("X-Total-Count") == str(body["total"])


def test_get_regras_atributos(client_regras_dnd5e):
    r = client_regras_dnd5e.get("/api/v1/dnd5e/regras/atributos")
    assert r.status_code == 200
    body = r.json()
    assert body["habilidade_min"] == 1
    assert body["habilidade_max"] == 25
    assert body["nivel_min"] == 1
    assert body["nivel_max"] == 20
    assert body["formula_modificador"] == "(valor - 10) // 2"
    assert len(body["habilidades"]) == 6
    assert body["habilidades"][0]["chave"] == "strength"
    assert body["habilidades"][0]["nome"] == "Força"
    assert body["habilidades"][0]["abreviacao_en"] == "STR"
    assert body["habilidades"][-1]["chave"] == "charisma"
    assert len(body["bonus_proficiencia_por_nivel"]) == 5
    assert body["bonus_proficiencia_por_nivel"][0] == {
        "nivel_min": 1,
        "nivel_max": 4,
        "bonus": 2,
    }
    assert body["bonus_proficiencia_por_nivel"][-1]["bonus"] == 6


class _DummyUser:
    id = 42
    email = "dummy@test"


def _build_strict_probe_app():
    app = FastAPI()
    app.include_router(dnd5e_regras_router, prefix="/api/v1")
    app.dependency_overrides[get_usuario_atual] = lambda: _DummyUser()
    return app


def test_requer_game_dnd5e_strict_off_aceita_token_sem_game_slug(monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", False)
    client = TestClient(_build_strict_probe_app())
    from app.shared.core.security import criar_token

    token = criar_token(
        data={"sub": "dummy@test"},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    r = client.get(
        "/api/v1/dnd5e/regras/atributos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200


def test_requer_game_dnd5e_strict_on_sem_game_slug_409(monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)
    client = TestClient(_build_strict_probe_app())
    from app.shared.core.security import criar_token

    token = criar_token(
        data={"sub": "dummy@test"},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    r = client.get(
        "/api/v1/dnd5e/regras/atributos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 409
    assert r.headers.get("X-Game-Slug-Required") == GAME_SLUG_DND5E


def test_requer_game_dnd5e_strict_on_slug_errado_403(monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)
    client = TestClient(_build_strict_probe_app())
    from app.shared.core.security import criar_token

    token = criar_token(
        data={"sub": "dummy@test", "game_slug": "dnd35"},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    r = client.get(
        "/api/v1/dnd5e/regras/atributos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403


def test_requer_game_dnd5e_strict_on_dnd5e_ok(monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)
    client = TestClient(_build_strict_probe_app())
    from app.shared.core.security import criar_token

    token = criar_token(
        data={"sub": "dummy@test", "game_slug": GAME_SLUG_DND5E},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    r = client.get(
        "/api/v1/dnd5e/regras/atributos",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200


def test_requer_game_dnd5e_probe_endpoint(monkeypatch):
    """Guard isolado (sem router de regras) — paridade com test_games_multi_api."""
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)
    app = FastAPI()

    @app.get("/probe")
    def probe(_usuario: Usuario = Depends(requer_game_dnd5e)):
        return {"ok": True}

    app.dependency_overrides[get_usuario_atual] = lambda: _DummyUser()
    client = TestClient(app)
    from app.shared.core.security import criar_token

    token = criar_token(
        data={"sub": "dummy@test", "game_slug": GAME_SLUG_DND5E},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    r = client.get("/probe", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["ok"] is True
