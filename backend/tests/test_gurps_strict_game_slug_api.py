"""Modo estrito multi-jogo — endpoints GURPS exigem claim `game_slug=gurps` no JWT."""

from __future__ import annotations

from typing import Sequence

import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from app.games.gurps.api.v1.campanhas import router as gurps_campanhas_router
from app.games.gurps.api.v1.combate import router as gurps_combate_router
from app.games.gurps.api.v1.personagens import router as gurps_personagens_router
from app.shared.constants import GAME_SLUG_DND35, GAME_SLUG_GURPS
from app.shared.core.config import settings
from app.shared.core.database import get_db
from app.shared.core.security import criar_token


def _build_app_with_real_auth(SessionLocal, routers: Sequence[APIRouter]) -> FastAPI:
    app = FastAPI()
    for router in routers:
        app.include_router(router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    return app


def test_strict_sem_game_slug_retorna_409(gurps_personagens_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, u1, _ = gurps_personagens_db
    app = _build_app_with_real_auth(SessionLocal, [gurps_personagens_router])
    client = TestClient(app)

    token = criar_token(
        data={"sub": u1.email},
        secret_key=settings.SECRET_KEY,
    )
    r = client.get(
        "/api/v1/gurps/personagens",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 409
    assert "jogo" in r.json().get("detail", "").lower()


def test_strict_game_slug_errado_retorna_403(gurps_personagens_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, u1, _ = gurps_personagens_db
    app = _build_app_with_real_auth(SessionLocal, [gurps_personagens_router])
    client = TestClient(app)

    token = criar_token(
        data={"sub": u1.email, "game_slug": GAME_SLUG_DND35},
        secret_key=settings.SECRET_KEY,
    )
    r = client.get(
        "/api/v1/gurps/personagens",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 403
    assert GAME_SLUG_GURPS in r.json().get("detail", "") or "gurps" in r.json().get("detail", "").lower()


def test_strict_game_slug_gurps_permite_listar(gurps_personagens_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, u1, _ = gurps_personagens_db
    app = _build_app_with_real_auth(SessionLocal, [gurps_personagens_router])
    client = TestClient(app)

    token = criar_token(
        data={"sub": u1.email, "game_slug": GAME_SLUG_GURPS},
        secret_key=settings.SECRET_KEY,
    )
    r = client.get(
        "/api/v1/gurps/personagens",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_strict_campanhas_sem_game_slug_retorna_409(gurps_mestre_e_jogadores_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, mestre, _, _ = gurps_mestre_e_jogadores_db
    app = _build_app_with_real_auth(SessionLocal, [gurps_campanhas_router])
    client = TestClient(app)

    token = criar_token(
        data={"sub": mestre.email},
        secret_key=settings.SECRET_KEY,
    )
    r = client.get(
        "/api/v1/gurps/campanhas",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 409


def test_strict_combate_status_sem_game_slug_retorna_409(gurps_personagens_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, u1, _ = gurps_personagens_db
    app = _build_app_with_real_auth(SessionLocal, [gurps_combate_router])
    client = TestClient(app)

    token = criar_token(
        data={"sub": u1.email},
        secret_key=settings.SECRET_KEY,
    )
    r = client.get(
        "/api/v1/gurps/combate/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 409


def test_strict_campanhas_com_slug_gurps_permite_mestre(gurps_mestre_e_jogadores_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, mestre, _, _ = gurps_mestre_e_jogadores_db
    app = _build_app_with_real_auth(SessionLocal, [gurps_campanhas_router])
    client = TestClient(app)

    token = criar_token(
        data={"sub": mestre.email, "game_slug": GAME_SLUG_GURPS},
        secret_key=settings.SECRET_KEY,
    )
    r = client.get(
        "/api/v1/gurps/campanhas",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_strict_post_campanha_sem_game_slug_retorna_409(gurps_mestre_e_jogadores_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, mestre, _, _ = gurps_mestre_e_jogadores_db
    app = _build_app_with_real_auth(SessionLocal, [gurps_campanhas_router])
    client = TestClient(app)

    token = criar_token(
        data={"sub": mestre.email},
        secret_key=settings.SECRET_KEY,
    )
    r = client.post(
        "/api/v1/gurps/campanhas",
        headers={"Authorization": f"Bearer {token}"},
        json={"nome": "Bloqueada"},
    )
    assert r.status_code == 409


def test_strict_post_campanha_com_slug_gurps_cria_201(gurps_mestre_e_jogadores_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, mestre, _, _ = gurps_mestre_e_jogadores_db
    app = _build_app_with_real_auth(SessionLocal, [gurps_campanhas_router])
    client = TestClient(app)

    token = criar_token(
        data={"sub": mestre.email, "game_slug": GAME_SLUG_GURPS},
        secret_key=settings.SECRET_KEY,
    )
    r = client.post(
        "/api/v1/gurps/campanhas",
        headers={"Authorization": f"Bearer {token}"},
        json={"nome": "Campanha JWT strict", "descricao": "integração"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["nome"] == "Campanha JWT strict"
    assert body["mestre_id"] == mestre.id
