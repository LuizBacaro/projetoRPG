from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.shared.api.v1.usuarios import router as usuarios_router
from app.shared.core.database import Base, get_db
from app.shared.core.deps import requer_admin
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario, Usuario


@pytest.fixture(scope="function")
def usuarios_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )

    db = testing_session_local()
    try:
        yield db, testing_session_local
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _criar_usuario(
    db,
    *,
    perfil: PerfilUsuario,
    nome: str,
    email: str,
    ativo: bool = True,
) -> Usuario:
    usuario = Usuario(
        perfil=perfil,
        nome=nome,
        email=email,
        senha_hash=hash_senha("SenhaSegura123"),
        ativo=ativo,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _build_client(test_db_factory, usuario_admin_atual):
    app = FastAPI()
    app.include_router(usuarios_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[requer_admin] = lambda: usuario_admin_atual
    return TestClient(app)


def test_delete_definitivo_remove_usuario_com_204(usuarios_db):
    test_db, test_db_factory = usuarios_db

    _criar_usuario(
        test_db,
        perfil=PerfilUsuario.ADMINISTRADOR,
        nome="Admin Atual",
        email="admin.atual@example.com",
    )
    alvo = _criar_usuario(
        test_db,
        perfil=PerfilUsuario.JOGADOR,
        nome="Jogador Alvo",
        email="jogador.alvo@example.com",
    )

    admin_atual = SimpleNamespace(
        id=999,
        email="admin.executor@example.com",
        perfil=PerfilUsuario.ADMINISTRADOR,
    )

    client = _build_client(test_db_factory, admin_atual)

    response = client.delete(f"/api/v1/usuarios/{alvo.id}/definitivo")

    assert response.status_code == 204
    db_validacao = test_db_factory()
    try:
        assert db_validacao.query(Usuario).filter(Usuario.id == alvo.id).first() is None
    finally:
        db_validacao.close()


def test_delete_definitivo_bloqueia_autoexclusao(usuarios_db):
    test_db, test_db_factory = usuarios_db

    admin_atual = _criar_usuario(
        test_db,
        perfil=PerfilUsuario.ADMINISTRADOR,
        nome="Admin Atual",
        email="admin.atual@example.com",
    )

    client = _build_client(test_db_factory, admin_atual)

    response = client.delete(f"/api/v1/usuarios/{admin_atual.id}/definitivo")

    assert response.status_code == 403
    assert response.json()["detail"] == "Você não pode excluir o próprio usuário logado"


def test_delete_definitivo_bloqueia_ultimo_admin_ativo(usuarios_db):
    test_db, test_db_factory = usuarios_db

    admin_alvo = _criar_usuario(
        test_db,
        perfil=PerfilUsuario.ADMINISTRADOR,
        nome="Admin Único",
        email="admin.unico@example.com",
    )

    # Admin autenticado não está persistido, então o banco ainda tem 1 admin ativo.
    admin_atual = SimpleNamespace(
        id=999,
        email="admin.executor@example.com",
        perfil=PerfilUsuario.ADMINISTRADOR,
    )

    client = _build_client(test_db_factory, admin_atual)

    response = client.delete(f"/api/v1/usuarios/{admin_alvo.id}/definitivo")

    assert response.status_code == 409
    assert (
        response.json()["detail"]
        == "Não é possível excluir o último administrador ativo"
    )


def test_delete_padrao_inativa_usuario_sem_excluir(usuarios_db):
    test_db, test_db_factory = usuarios_db

    _criar_usuario(
        test_db,
        perfil=PerfilUsuario.ADMINISTRADOR,
        nome="Admin Atual",
        email="admin.atual@example.com",
    )
    alvo = _criar_usuario(
        test_db,
        perfil=PerfilUsuario.JOGADOR,
        nome="Jogador Alvo",
        email="jogador.alvo@example.com",
    )

    admin_atual = SimpleNamespace(
        id=999,
        email="admin.executor@example.com",
        perfil=PerfilUsuario.ADMINISTRADOR,
    )

    client = _build_client(test_db_factory, admin_atual)

    response = client.delete(f"/api/v1/usuarios/{alvo.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == alvo.id
    assert payload["ativo"] is False

    db_validacao = test_db_factory()
    try:
        usuario_db = db_validacao.query(Usuario).filter(Usuario.id == alvo.id).first()
        assert usuario_db is not None
        assert usuario_db.ativo is False
    finally:
        db_validacao.close()
