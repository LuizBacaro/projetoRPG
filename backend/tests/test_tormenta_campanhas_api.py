"""Integração HTTP — campanhas Tormenta 20."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.tormenta.api.v1.campanhas import router as tormenta_campanhas_router
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.shared.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario, Usuario


@pytest.fixture(scope="function")
def tormenta_mestre_e_jogador_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    import app.models  # noqa: F401

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        jog = Usuario(
            perfil=PerfilUsuario.JOGADOR,
            nome="T20 Jog Camp",
            email="t20camp.jog@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        mestre = Usuario(
            perfil=PerfilUsuario.MESTRE,
            nome="T20 Mestre Camp",
            email="t20camp.mestre@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add_all([jog, mestre])
        db.commit()
        db.refresh(jog)
        db.refresh(mestre)
        yield SessionLocal, mestre, jog
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _usuario(u: Usuario) -> SimpleNamespace:
    return SimpleNamespace(id=u.id, perfil=u.perfil, email=u.email, nome=u.nome)


def _client(SessionLocal, usuario: SimpleNamespace) -> TestClient:
    app = FastAPI()
    app.include_router(tormenta_campanhas_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    return TestClient(app)


def test_jogador_403_listar_campanhas(tormenta_mestre_e_jogador_db):
    SessionLocal, _m, jog = tormenta_mestre_e_jogador_db
    c = _client(SessionLocal, _usuario(jog))
    r = c.get("/api/v1/tormenta/campanhas")
    assert r.status_code == 403


def test_mestre_cria_lista_e_sessao(tormenta_mestre_e_jogador_db):
    SessionLocal, mestre, jog = tormenta_mestre_e_jogador_db
    db = SessionLocal()
    p1 = TormentaPersonagem(
        dono_id=jog.id,
        tipo="jogador",
        nome="Herói T20",
        ficha_json={},
    )
    db.add(p1)
    db.commit()
    db.refresh(p1)
    db.close()

    c_m = _client(SessionLocal, _usuario(mestre))
    r = c_m.post(
        "/api/v1/tormenta/campanhas",
        json={
            "nome": "Mesa Tormenta",
            "descricao": "Integração",
            "personagem_ids": [p1.id],
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    cid = body["id"]
    assert body["personagem_ids"] == [p1.id]

    r2 = c_m.post(
        "/api/v1/tormenta/campanhas/sessoes",
        json={
            "campanha_id": cid,
            "resumo": "Primeira sessão: teste.",
            "visivel_jogadores": True,
        },
    )
    assert r2.status_code == 201, r2.text
    sid = r2.json()["id"]

    rs = c_m.get("/api/v1/tormenta/campanhas/sessoes")
    assert rs.status_code == 200
    assert any(s["id"] == sid for s in rs.json())

    c_j = _client(SessionLocal, _usuario(jog))
    rv = c_j.get("/api/v1/tormenta/campanhas/sessoes/visiveis")
    assert rv.status_code == 200
    assert any(s["id"] == sid for s in rv.json())
