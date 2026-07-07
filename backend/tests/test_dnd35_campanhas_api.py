"""Integração HTTP — campanhas D&D 3.5."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd35.api.v1.campanhas import router as dnd35_campanhas_router
from app.shared.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario, Usuario


@pytest.fixture(scope="function")
def dnd35_mestre_e_jogador_db():
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
            nome="D35 Jog Camp",
            email="d35camp.jog@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        mestre = Usuario(
            perfil=PerfilUsuario.MESTRE,
            nome="D35 Mestre Camp",
            email="d35camp.mestre@example.com",
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
    app.include_router(dnd35_campanhas_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    return TestClient(app)


def test_jogador_lista_campanhas_vazias(dnd35_mestre_e_jogador_db):
    SessionLocal, _m, jog = dnd35_mestre_e_jogador_db
    c = _client(SessionLocal, _usuario(jog))
    r = c.get("/api/v1/campanhas")
    assert r.status_code == 200
    assert r.json() == []


def test_jogador_cria_e_lista_propria_campanha(dnd35_mestre_e_jogador_db):
    SessionLocal, _m, jog = dnd35_mestre_e_jogador_db
    c = _client(SessionLocal, _usuario(jog))
    r = c.post(
        "/api/v1/campanhas",
        json={"nome": "Mesa do Jogador", "descricao": "Primeira campanha"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["nome"] == "Mesa do Jogador"

    r2 = c.get("/api/v1/campanhas")
    assert r2.status_code == 200
    lista = r2.json()
    assert len(lista) == 1
    assert lista[0]["id"] == body["id"]


def test_mestre_legado_cria_campanha(dnd35_mestre_e_jogador_db):
    SessionLocal, mestre, _jog = dnd35_mestre_e_jogador_db
    c = _client(SessionLocal, _usuario(mestre))
    r = c.post(
        "/api/v1/campanhas",
        json={"nome": "Mesa Legado", "descricao": ""},
    )
    assert r.status_code == 201, r.text
    assert r.json()["nome"] == "Mesa Legado"


def test_solicitacao_entrada_campanha_aceite_pelo_mestre(dnd35_mestre_e_jogador_db):
    from app.games.dnd35.models.combatente import Combatente

    SessionLocal, mestre, jog = dnd35_mestre_e_jogador_db
    db = SessionLocal()
    comb = Combatente(
        dono_id=jog.id,
        tipo="jogador",
        nome="Herói D35",
        classe="Guerreiro",
        hp_atual=10,
        hp_maximo=10,
    )
    db.add(comb)
    db.commit()
    db.refresh(comb)
    db.close()

    c_mestre = _client(SessionLocal, _usuario(mestre))
    c_jog = _client(SessionLocal, _usuario(jog))

    cid = c_mestre.post(
        "/api/v1/campanhas", json={"nome": "Mesa Solicitacao D35"}
    ).json()["id"]

    r_sol = c_jog.post(
        "/api/v1/campanhas/solicitacoes",
        json={"campanha_id": cid, "personagem_id": comb.id},
    )
    assert r_sol.status_code == 201, r_sol.text
    sid = r_sol.json()["id"]

    r_pend = c_mestre.get("/api/v1/campanhas/solicitacoes/pendentes")
    assert any(x["id"] == sid for x in r_pend.json())

    r_ok = c_mestre.post(f"/api/v1/campanhas/solicitacoes/{sid}/aceitar")
    assert r_ok.status_code == 200

    db = SessionLocal()
    atualizado = db.query(Combatente).filter(Combatente.id == comb.id).first()
    assert atualizado.campanha_id == cid
    db.close()


def test_listar_disponiveis_retorna_campanhas(dnd35_mestre_e_jogador_db):
    SessionLocal, mestre, jog = dnd35_mestre_e_jogador_db
    c_mestre = _client(SessionLocal, _usuario(mestre))
    c_jog = _client(SessionLocal, _usuario(jog))
    c_mestre.post("/api/v1/campanhas", json={"nome": "Camp Publica D35"})
    r = c_jog.get("/api/v1/campanhas/disponiveis")
    assert r.status_code == 200
    assert "Camp Publica D35" in {c["nome"] for c in r.json()}
