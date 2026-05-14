"""HTTP — combate Tormenta (Arena): RBAC mestre/administrador."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.tormenta.api.v1.combate import router as tormenta_combate_router
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario, Usuario as UModel


@pytest.fixture(scope="function")
def tormenta_combate_api_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    import app.models  # noqa: F401
    from app.shared.core.database import Base

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        u_jog = UModel(
            perfil=PerfilUsuario.JOGADOR,
            nome="T20 Jog",
            email="t20combate.jog@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        u_mestre = UModel(
            perfil=PerfilUsuario.MESTRE,
            nome="T20 Mestre",
            email="t20combate.mestre@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        u_admin = UModel(
            perfil=PerfilUsuario.ADMINISTRADOR,
            nome="T20 Admin",
            email="t20combate.admin@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add_all([u_jog, u_mestre, u_admin])
        db.commit()
        db.refresh(u_jog)
        db.refresh(u_mestre)
        db.refresh(u_admin)
        yield SessionLocal, u_jog, u_mestre, u_admin
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _client(SessionLocal, usuario: UModel) -> TestClient:
    app = FastAPI()
    app.include_router(tormenta_combate_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    return TestClient(app)


def test_combate_status_403_para_jogador(tormenta_combate_api_db):
    SessionLocal, u_jog, _u_m, _u_a = tormenta_combate_api_db
    c = _client(SessionLocal, u_jog)
    r = c.get("/api/v1/tormenta/combate/status")
    assert r.status_code == 403
    assert "mestre" in (r.json().get("detail") or "").lower()


def test_combate_status_200_para_mestre(tormenta_combate_api_db):
    SessionLocal, _u_j, u_m, _u_a = tormenta_combate_api_db
    c = _client(SessionLocal, u_m)
    r = c.get("/api/v1/tormenta/combate/status")
    assert r.status_code == 200
    body = r.json()
    assert body.get("ativo") is False


def test_combate_status_200_para_administrador(tormenta_combate_api_db):
    SessionLocal, _u_j, _u_m, u_a = tormenta_combate_api_db
    c = _client(SessionLocal, u_a)
    r = c.get("/api/v1/tormenta/combate/status")
    assert r.status_code == 200
