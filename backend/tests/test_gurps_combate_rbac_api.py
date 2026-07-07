"""HTTP — combate GURPS: RBAC mestre por campanha ou perfil legado."""

from __future__ import annotations

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.gurps.api.v1.combate import router as gurps_combate_router
from app.games.gurps.models.campanha import GurpsCampanha
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario
from app.shared.models.usuario import Usuario as UModel


@pytest.fixture(scope="function")
def gurps_combate_rbac_db():
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
            nome="GURPS Jog RBAC",
            email="gurpscombate.jog@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        u_mestre = UModel(
            perfil=PerfilUsuario.MESTRE,
            nome="GURPS Mestre RBAC",
            email="gurpscombate.mestre@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add_all([u_jog, u_mestre])
        db.commit()
        db.refresh(u_jog)
        db.refresh(u_mestre)
        yield SessionLocal, u_jog, u_mestre
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _client(SessionLocal, usuario: UModel) -> TestClient:
    app = FastAPI()
    app.include_router(gurps_combate_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    return TestClient(app)


def test_combate_status_403_para_jogador_sem_campanha(gurps_combate_rbac_db):
    SessionLocal, u_jog, _u_m = gurps_combate_rbac_db
    c = _client(SessionLocal, u_jog)
    r = c.get("/api/v1/gurps/combate/status")
    assert r.status_code == 403
    assert "campanha" in (r.json().get("detail") or "").lower()


def test_combate_status_200_para_jogador_com_campanha(gurps_combate_rbac_db):
    SessionLocal, u_jog, _u_m = gurps_combate_rbac_db
    db = SessionLocal()
    db.add(
        GurpsCampanha(
            mestre_id=u_jog.id,
            nome="Mesa teste",
            descricao="",
        )
    )
    db.commit()
    db.close()

    c = _client(SessionLocal, u_jog)
    r = c.get("/api/v1/gurps/combate/status")
    assert r.status_code == 200


def test_combate_status_200_para_mestre_legado(gurps_combate_rbac_db):
    SessionLocal, _u_j, u_m = gurps_combate_rbac_db
    c = _client(SessionLocal, u_m)
    r = c.get("/api/v1/gurps/combate/status")
    assert r.status_code == 200
