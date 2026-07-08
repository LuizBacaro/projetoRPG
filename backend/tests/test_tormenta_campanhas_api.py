"""Integração HTTP — campanhas Tormenta 20."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.tormenta.api.v1.campanhas import router as tormenta_campanhas_router
from app.games.tormenta.api.v1.personagens import router as tormenta_personagens_router
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
    app.include_router(tormenta_personagens_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    return TestClient(app)


def test_jogador_lista_campanhas_vazias(tormenta_mestre_e_jogador_db):
    SessionLocal, _m, jog = tormenta_mestre_e_jogador_db
    c = _client(SessionLocal, _usuario(jog))
    r = c.get("/api/v1/tormenta/campanhas")
    assert r.status_code == 200
    assert r.json() == []


def test_jogador_cria_e_lista_propria_campanha(tormenta_mestre_e_jogador_db):
    SessionLocal, _m, jog = tormenta_mestre_e_jogador_db
    c = _client(SessionLocal, _usuario(jog))
    r = c.post(
        "/api/v1/tormenta/campanhas",
        json={"nome": "Mesa do Jogador", "descricao": "Primeira campanha"},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["nome"] == "Mesa do Jogador"
    assert body["mestre_id"] == jog.id

    r2 = c.get("/api/v1/tormenta/campanhas")
    assert r2.status_code == 200
    lista = r2.json()
    assert len(lista) == 1
    assert lista[0]["id"] == body["id"]


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


def test_mestre_de_campanha_lista_somente_proprios_sem_campanha_id(
    tormenta_mestre_e_jogador_db,
):
    """Dono de campanha (perfil jogador) não vê personagens alheios na aba Combatentes."""
    SessionLocal, _mestre, jog = tormenta_mestre_e_jogador_db
    db = SessionLocal()
    p_jog = TormentaPersonagem(
        dono_id=jog.id, tipo="jogador", nome="Meu Herói", ficha_json={}
    )
    p_outro = TormentaPersonagem(
        dono_id=_mestre.id, tipo="jogador", nome="Outro Herói", ficha_json={}
    )
    db.add_all([p_jog, p_outro])
    db.commit()
    db.refresh(p_jog)
    db.close()

    c_jog = _client(SessionLocal, _usuario(jog))
    r_camp = c_jog.post(
        "/api/v1/tormenta/campanhas",
        json={"nome": "Mesa RBAC", "personagem_ids": [p_jog.id]},
    )
    assert r_camp.status_code == 201

    r_list = c_jog.get("/api/v1/tormenta/personagens")
    assert r_list.status_code == 200
    nomes = {p["nome"] for p in r_list.json()}
    assert "Meu Herói" in nomes
    assert "Outro Herói" not in nomes


def test_listar_por_campanha_id_inclui_participantes(tormenta_mestre_e_jogador_db):
    SessionLocal, _mestre, jog = tormenta_mestre_e_jogador_db
    db = SessionLocal()
    p_jog = TormentaPersonagem(
        dono_id=jog.id, tipo="jogador", nome="Jogador A", ficha_json={}
    )
    p_npc = TormentaPersonagem(dono_id=None, tipo="npc", nome="NPC Mesa", ficha_json={})
    db.add_all([p_jog, p_npc])
    db.commit()
    db.refresh(p_jog)
    db.refresh(p_npc)
    db.close()

    c_jog = _client(SessionLocal, _usuario(jog))
    cid = c_jog.post(
        "/api/v1/tormenta/campanhas",
        json={"nome": "Mesa Lista", "personagem_ids": [p_jog.id]},
    ).json()["id"]

    db = SessionLocal()
    p_npc.campanha_id = cid
    db.add(p_npc)
    db.commit()
    db.close()

    r = c_jog.get(f"/api/v1/tormenta/personagens?campanha_id={cid}")
    assert r.status_code == 200
    nomes = {p["nome"] for p in r.json()}
    assert nomes == {"Jogador A", "NPC Mesa"}


def test_criar_monstro_com_campanha_id_vincula_mesa(tormenta_mestre_e_jogador_db):
    SessionLocal, _mestre, jog = tormenta_mestre_e_jogador_db
    c_jog = _client(SessionLocal, _usuario(jog))
    cid = c_jog.post("/api/v1/tormenta/campanhas", json={"nome": "Mesa Criar"}).json()[
        "id"
    ]

    r = c_jog.post(
        "/api/v1/tormenta/personagens",
        json={
            "nome": "Goblin",
            "tipo": "monstro",
            "campanha_id": cid,
            "for_valor": 10,
            "des_valor": 10,
            "con_valor": 10,
            "int_valor": 10,
            "sab_valor": 10,
            "car_valor": 10,
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["campanha_id"] == cid
    assert body["tipo"] == "monstro"


def test_solicitacao_entrada_campanha_aceite_pelo_mestre(tormenta_mestre_e_jogador_db):
    SessionLocal, mestre, jog = tormenta_mestre_e_jogador_db
    db = SessionLocal()
    p_jog = TormentaPersonagem(
        dono_id=jog.id, tipo="jogador", nome="Herói Sol", ficha_json={}
    )
    db.add(p_jog)
    db.commit()
    db.refresh(p_jog)
    db.close()

    c_mestre = _client(SessionLocal, _usuario(mestre))
    c_jog = _client(SessionLocal, _usuario(jog))

    cid = c_mestre.post(
        "/api/v1/tormenta/campanhas", json={"nome": "Mesa Solicitacao"}
    ).json()["id"]

    r_sol = c_jog.post(
        "/api/v1/tormenta/campanhas/solicitacoes",
        json={"campanha_id": cid, "personagem_id": p_jog.id},
    )
    assert r_sol.status_code == 201, r_sol.text
    body = r_sol.json()
    assert body["status"] == "pendente"
    sid = body["id"]

    r_pend = c_mestre.get("/api/v1/tormenta/campanhas/solicitacoes/pendentes")
    assert r_pend.status_code == 200
    assert any(x["id"] == sid for x in r_pend.json())

    r_ok = c_mestre.post(f"/api/v1/tormenta/campanhas/solicitacoes/{sid}/aceitar")
    assert r_ok.status_code == 200
    assert r_ok.json()["status"] == "aceita"

    r_p = c_jog.get(f"/api/v1/tormenta/personagens/{p_jog.id}")
    assert r_p.json()["campanha_id"] == cid


def test_solicitacao_recusada_aparece_no_historico(tormenta_mestre_e_jogador_db):
    SessionLocal, mestre, jog = tormenta_mestre_e_jogador_db
    db = SessionLocal()
    p_jog = TormentaPersonagem(
        dono_id=jog.id, tipo="jogador", nome="Herói Lua", ficha_json={}
    )
    db.add(p_jog)
    db.commit()
    db.refresh(p_jog)
    db.close()

    c_mestre = _client(SessionLocal, _usuario(mestre))
    c_jog = _client(SessionLocal, _usuario(jog))

    cid = c_mestre.post(
        "/api/v1/tormenta/campanhas", json={"nome": "Mesa Historico"}
    ).json()["id"]

    sid = c_jog.post(
        "/api/v1/tormenta/campanhas/solicitacoes",
        json={"campanha_id": cid, "personagem_id": p_jog.id},
    ).json()["id"]

    r_rec = c_mestre.post(f"/api/v1/tormenta/campanhas/solicitacoes/{sid}/recusar")
    assert r_rec.status_code == 200
    assert r_rec.json()["status"] == "recusada"

    r_pend = c_mestre.get("/api/v1/tormenta/campanhas/solicitacoes/pendentes")
    assert all(x["id"] != sid for x in r_pend.json())

    r_hist = c_mestre.get("/api/v1/tormenta/campanhas/solicitacoes/historico")
    assert r_hist.status_code == 200
    hist = r_hist.json()
    achado = next((x for x in hist if x["id"] == sid), None)
    assert achado is not None
    assert achado["status"] == "recusada"


def test_listar_disponiveis_retorna_campanhas(tormenta_mestre_e_jogador_db):
    SessionLocal, mestre, jog = tormenta_mestre_e_jogador_db
    c_mestre = _client(SessionLocal, _usuario(mestre))
    c_jog = _client(SessionLocal, _usuario(jog))
    c_mestre.post("/api/v1/tormenta/campanhas", json={"nome": "Camp Publica"})
    r = c_jog.get("/api/v1/tormenta/campanhas/disponiveis")
    assert r.status_code == 200
    nomes = {c["nome"] for c in r.json()}
    assert "Camp Publica" in nomes
