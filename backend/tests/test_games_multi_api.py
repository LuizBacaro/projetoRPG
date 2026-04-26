"""
Testes da camada multi-jogo: catálogo, seleção de jogo e guard `requer_game_dnd35`.
"""
from __future__ import annotations

from datetime import timedelta

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.auth import router as auth_router
from app.api.v1.games import router as games_router
from app.core.config import settings
from app.core.database import Base, get_db
from app.core.deps import get_usuario_atual, requer_game_dnd35
from app.core.security import decodificar_token, hash_senha
from app.models.game import Game, UserGameMembership
from app.models.usuario import PerfilUsuario, Usuario
from app.shared.constants import GAME_SLUG_DND35


@pytest.fixture(scope="function")
def hub_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    try:
        yield db, TestingSessionLocal
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _seed_catalog_and_user(db):
    g35 = Game(
        slug="dnd35",
        nome="D&D 3.5",
        status="disponivel",
        ordem=1,
    )
    g5e = Game(
        slug="dnd5e",
        nome="D&D 5e",
        status="em_breve",
        ordem=2,
    )
    db.add_all([g35, g5e])
    db.commit()
    db.refresh(g35)

    u = Usuario(
        perfil=PerfilUsuario.JOGADOR,
        nome="Jogador Teste",
        email="jogador.games@example.com",
        senha_hash=hash_senha("SenhaSegura123"),
        ativo=True,
    )
    db.add(u)
    db.commit()
    db.refresh(u)

    m = UserGameMembership(
        usuario_id=u.id,
        game_id=g35.id,
        perfil_no_jogo=PerfilUsuario.JOGADOR.value,
        ativo=True,
    )
    db.add(m)
    db.commit()

    admin = Usuario(
        perfil=PerfilUsuario.ADMINISTRADOR,
        nome="Admin Teste",
        email="admin.games@example.com",
        senha_hash=hash_senha("AdminSegura456"),
        ativo=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    db.add(
        UserGameMembership(
            usuario_id=admin.id,
            game_id=g35.id,
            perfil_no_jogo=PerfilUsuario.ADMINISTRADOR.value,
            ativo=True,
        )
    )
    db.commit()

    return u, admin, g35, g5e


def _build_hub_client(test_db_factory):
    app = FastAPI()
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(games_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


def test_get_games_sem_token_401(hub_db):
    db, factory = hub_db
    _seed_catalog_and_user(db)

    client = _build_hub_client(factory)
    r = client.get("/api/v1/games")
    assert r.status_code == 401


def test_get_games_com_login_sem_game_slug_ativo_null(hub_db):
    db, factory = hub_db
    _seed_catalog_and_user(db)

    client = _build_hub_client(factory)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "jogador.games@example.com", "senha": "SenhaSegura123"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]
    payload = decodificar_token(token, settings.SECRET_KEY)
    assert payload is not None
    assert "game_slug" not in payload or payload.get("game_slug") is None

    r = client.get("/api/v1/games", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    body = r.json()
    assert body["game_slug_ativo"] is None
    assert any(j["slug"] == "dnd35" for j in body["jogos"])


def test_post_selecionar_dnd35_emite_claims_no_jwt(hub_db):
    db, factory = hub_db
    _seed_catalog_and_user(db)

    client = _build_hub_client(factory)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "jogador.games@example.com", "senha": "SenhaSegura123"},
    )
    token = login.json()["access_token"]

    r = client.post(
        "/api/v1/games/selecionar",
        headers={"Authorization": f"Bearer {token}"},
        json={"game_slug": "dnd35"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["game_slug"] == "dnd35"
    assert data["access_token"]

    payload = decodificar_token(data["access_token"], settings.SECRET_KEY)
    assert payload is not None
    assert payload.get("game_slug") == "dnd35"
    assert payload.get("perfil_no_jogo") == PerfilUsuario.JOGADOR.value
    assert payload.get("profile") == PerfilUsuario.JOGADOR.value


def test_post_selecionar_jogo_em_breve_retorna_409(hub_db):
    db, factory = hub_db
    _seed_catalog_and_user(db)

    client = _build_hub_client(factory)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "jogador.games@example.com", "senha": "SenhaSegura123"},
    )
    token = login.json()["access_token"]

    r = client.post(
        "/api/v1/games/selecionar",
        headers={"Authorization": f"Bearer {token}"},
        json={"game_slug": "dnd5e"},
    )
    assert r.status_code == 409


def test_get_games_apos_selecionar_informa_game_slug_ativo(hub_db):
    db, factory = hub_db
    _seed_catalog_and_user(db)

    client = _build_hub_client(factory)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "jogador.games@example.com", "senha": "SenhaSegura123"},
    )
    token = login.json()["access_token"]
    sel = client.post(
        "/api/v1/games/selecionar",
        headers={"Authorization": f"Bearer {token}"},
        json={"game_slug": "dnd35"},
    )
    token2 = sel.json()["access_token"]

    r = client.get("/api/v1/games", headers={"Authorization": f"Bearer {token2}"})
    assert r.status_code == 200
    assert r.json()["game_slug_ativo"] == "dnd35"


def test_admin_listar_memberships_dnd35(hub_db):
    db, factory = hub_db
    _seed_catalog_and_user(db)

    client = _build_hub_client(factory)
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin.games@example.com", "senha": "AdminSegura456"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    r = client.get(
        "/api/v1/games/dnd35/memberships",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert r.status_code == 200
    items = r.json()["items"]
    emails = {x["usuario_email"] for x in items}
    assert "jogador.games@example.com" in emails
    assert "admin.games@example.com" in emails


class _DummyUser:
    id = 42
    email = "dummy@test"


def _build_strict_probe_app():
    app = FastAPI()

    @app.get("/probe")
    def probe(_usuario: Usuario = Depends(requer_game_dnd35)):
        return {"ok": True, "email": _usuario.email}

    app.dependency_overrides[get_usuario_atual] = lambda: _DummyUser()
    return app


def test_requer_game_strict_off_aceita_token_sem_game_slug(monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", False)
    app = _build_strict_probe_app()
    client = TestClient(app)
    from app.core.security import criar_token

    token = criar_token(
        data={"sub": "dummy@test"},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    r = client.get("/probe", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_requer_game_strict_on_sem_game_slug_409(monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)
    app = _build_strict_probe_app()
    client = TestClient(app)
    from app.core.security import criar_token

    token = criar_token(
        data={"sub": "dummy@test"},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    r = client.get("/probe", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 409
    assert r.headers.get("X-Game-Slug-Required") == GAME_SLUG_DND35


def test_requer_game_strict_on_slug_errado_403(monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)
    app = _build_strict_probe_app()
    client = TestClient(app)
    from app.core.security import criar_token

    token = criar_token(
        data={"sub": "dummy@test", "game_slug": "dnd5e"},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    r = client.get("/probe", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 403


def test_requer_game_strict_on_dnd35_ok(monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)
    app = _build_strict_probe_app()
    client = TestClient(app)
    from app.core.security import criar_token

    token = criar_token(
        data={"sub": "dummy@test", "game_slug": "dnd35"},
        secret_key=settings.SECRET_KEY,
        expires_delta=timedelta(minutes=5),
        token_type="access",
    )
    r = client.get("/probe", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
