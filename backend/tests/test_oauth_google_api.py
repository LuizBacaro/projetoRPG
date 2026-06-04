"""OAuth Google e troca de código — rotas /auth/oauth."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.shared.api.v1 import oauth_google
from app.shared.api.v1.auth import router as auth_router
from app.shared.core.database import Base
from app.shared.core.deps import get_db
from app.shared.models.usuario import PerfilUsuario, Usuario
from app.shared.services.oauth_exchange_store import criar_exchange_code


@pytest.fixture(scope="function")
def oauth_db():
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


def _build_client(test_db_factory):
    app = FastAPI()

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(oauth_google.router, prefix="/api/v1")
    return TestClient(app)


def test_oauth_google_status_desabilitado_sem_credenciais(oauth_db):
    _, factory = oauth_db
    client = _build_client(factory)
    res = client.get("/api/v1/auth/oauth/google/status")
    assert res.status_code == 200
    assert res.json()["google_enabled"] is False


def test_oauth_exchange_codigo_invalido(oauth_db):
    _, factory = oauth_db
    client = _build_client(factory)
    res = client.post(
        "/api/v1/auth/oauth/exchange",
        json={"exchange_code": "codigo-inexistente"},
    )
    assert res.status_code == 401


def test_oauth_exchange_codigo_valido(oauth_db):
    _, factory = oauth_db
    client = _build_client(factory)
    payload = {
        "access_token": "a",
        "refresh_token": "r",
        "token_type": "bearer",
        "usuario": {
            "id": 1,
            "email": "g@example.com",
            "nome": "Google User",
            "perfil": "jogador",
            "ativo": True,
        },
    }
    code = criar_exchange_code(payload, ttl_seconds=60)
    res = client.post(
        "/api/v1/auth/oauth/exchange",
        json={"exchange_code": code},
    )
    assert res.status_code == 200
    body = res.json()
    assert body["access_token"] == "a"
    assert body["usuario"]["email"] == "g@example.com"


def test_login_conta_somente_google_rejeita_senha(oauth_db):
    db, factory = oauth_db
    db.add(
        Usuario(
            perfil=PerfilUsuario.JOGADOR,
            nome="OAuth Only",
            email="oauth@example.com",
            senha_hash=None,
            oauth_provider="google",
            oauth_subject="sub-123",
            ativo=True,
        )
    )
    db.commit()
    client = _build_client(factory)
    res = client.post(
        "/api/v1/auth/login",
        json={"email": "oauth@example.com", "senha": "qualquer123"},
    )
    assert res.status_code == 401
    assert "Google" in res.json()["detail"]
