from datetime import timedelta
from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.shared.api.v1.auth import router as auth_router
from app.shared.core.deps import get_db
from app.shared.core.security import criar_token, hash_senha
from app.shared.core.config import settings
from app.shared.core.database import Base
from app.shared.models.usuario import PerfilUsuario, Usuario


@pytest.fixture(scope="function")
def auth_db():
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
    app.include_router(auth_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    return TestClient(app)


def _create_user(test_db, *, email: str, senha: str, ativo: bool = True):
    usuario = Usuario(
        perfil=PerfilUsuario.JOGADOR,
        nome="Tester",
        email=email,
        senha_hash=hash_senha(senha),
        ativo=ativo,
    )
    test_db.add(usuario)
    test_db.commit()
    test_db.refresh(usuario)
    return usuario


def test_login_sucesso_retorna_tokens(auth_db):
    test_db, test_db_factory = auth_db
    _create_user(test_db, email="ok@example.com", senha="SenhaSegura123")
    client = _build_client(test_db_factory)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "ok@example.com", "senha": "SenhaSegura123"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["usuario"]["email"] == "ok@example.com"


def test_registro_publico_cria_jogador(auth_db):
    _, test_db_factory = auth_db
    client = _build_client(test_db_factory)

    response = client.post(
        "/api/v1/auth/registro",
        json={
            "nome": "Novo Jogador",
            "email": "novo_jogador@example.com",
            "senha": "SenhaSegura123",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["email"] == "novo_jogador@example.com"
    assert payload["perfil"] == "jogador"
    assert payload["ativo"] is True


def test_registro_publico_rejeita_email_duplicado(auth_db):
    test_db, test_db_factory = auth_db
    _create_user(test_db, email="duplicado@example.com", senha="SenhaSegura123")
    client = _build_client(test_db_factory)

    response = client.post(
        "/api/v1/auth/registro",
        json={
            "nome": "Outro Jogador",
            "email": "duplicado@example.com",
            "senha": "SenhaSegura123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "E-mail já cadastrado"


def test_login_falha_com_senha_incorreta(auth_db):
    test_db, test_db_factory = auth_db
    _create_user(test_db, email="badpass@example.com", senha="SenhaSegura123")
    client = _build_client(test_db_factory)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "badpass@example.com", "senha": "SenhaErrada999"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email ou senha incorretos"


def test_login_falha_com_usuario_inativo(auth_db):
    test_db, test_db_factory = auth_db
    _create_user(test_db, email="inactive@example.com", senha="SenhaSegura123", ativo=False)
    client = _build_client(test_db_factory)

    response = client.post(
        "/api/v1/auth/login",
        json={"email": "inactive@example.com", "senha": "SenhaSegura123"},
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Usuário inativo"


def test_refresh_com_token_invalido_retorna_401(auth_db):
    _, test_db_factory = auth_db
    client = _build_client(test_db_factory)

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": "token.invalido.aqui"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token inválido ou expirado"


def test_refresh_sucesso_gera_novos_tokens(auth_db):
    test_db, test_db_factory = auth_db
    usuario = _create_user(test_db, email="refresh@example.com", senha="SenhaSegura123")
    client = _build_client(test_db_factory)

    refresh_token = criar_token(
        {"sub": usuario.email},
        settings.SECRET_KEY,
        expires_delta=timedelta(days=1),
        token_type="refresh",
    )

    response = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["access_token"]
    assert payload["refresh_token"]
    assert payload["usuario"]["email"] == usuario.email


def test_me_retorna_usuario_autenticado(auth_db):
    test_db, test_db_factory = auth_db
    usuario = _create_user(test_db, email="me@example.com", senha="SenhaSegura123")
    client = _build_client(test_db_factory)

    access_token = criar_token(
        {"sub": usuario.email},
        settings.SECRET_KEY,
        expires_delta=timedelta(hours=1),
        token_type="access",
    )

    response = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == usuario.email