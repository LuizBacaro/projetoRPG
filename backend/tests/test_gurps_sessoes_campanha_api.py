"""Integração HTTP — sessões de campanha GURPS (mestre + leitura jogador)."""

from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.gurps.api.v1.campanhas import router as gurps_campanhas_router
from app.games.gurps.api.v1.personagens import router as gurps_personagens_router
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario, Usuario


def _usuario(u: Usuario) -> SimpleNamespace:
    return SimpleNamespace(id=u.id, perfil=u.perfil, email=u.email, nome=u.nome)


def _client(SessionLocal, usuario: SimpleNamespace) -> TestClient:
    app = FastAPI()
    app.include_router(gurps_personagens_router, prefix="/api/v1")
    app.include_router(gurps_campanhas_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    return TestClient(app)


def _criar_personagem(client: TestClient, nome: str) -> int:
    r = client.post(
        "/api/v1/gurps/personagens",
        json={"nome": nome, "tipo": "jogador", "extras": {}},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_jogador_nao_lista_todas_sessoes_apenas_mestre(gurps_mestre_e_jogadores_db):
    SessionLocal, _, j1, _ = gurps_mestre_e_jogadores_db
    c = _client(SessionLocal, _usuario(j1))
    r = c.get("/api/v1/gurps/campanhas/sessoes")
    assert r.status_code == 403


def test_mestre_crud_sessao_e_jogador_ve_visivel(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre, j1, j2 = gurps_mestre_e_jogadores_db
    c_m = _client(SessionLocal, _usuario(mestre))
    c_j1 = _client(SessionLocal, _usuario(j1))
    c_j2 = _client(SessionLocal, _usuario(j2))

    p1 = _criar_personagem(c_j1, "Herói")
    r_c = c_m.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Arco Teste", "personagem_ids": [p1]},
    )
    assert r_c.status_code == 201, r_c.text
    cid = r_c.json()["id"]

    r_priv = c_m.post(
        "/api/v1/gurps/campanhas/sessoes",
        json={
            "campanha_id": cid,
            "resumo": "Sessão secreta",
            "visivel_jogadores": False,
        },
    )
    assert r_priv.status_code == 201, r_priv.text

    vis = c_j1.get("/api/v1/gurps/campanhas/sessoes/visiveis").json()
    assert vis == []

    r_pub = c_m.post(
        "/api/v1/gurps/campanhas/sessoes",
        json={
            "campanha_id": cid,
            "resumo": "Resumo público",
            "visivel_jogadores": True,
        },
    )
    assert r_pub.status_code == 201, r_pub.text
    sid = r_pub.json()["id"]

    vis2 = c_j1.get("/api/v1/gurps/campanhas/sessoes/visiveis").json()
    assert len(vis2) == 1
    assert vis2[0]["id"] == sid
    assert vis2[0]["resumo"] == "Resumo público"
    assert vis2[0]["campanha_nome"] == "Arco Teste"

    assert c_j2.get("/api/v1/gurps/campanhas/sessoes/visiveis").json() == []

    r_put = c_m.put(
        f"/api/v1/gurps/campanhas/sessoes/{sid}",
        json={"visivel_jogadores": False},
    )
    assert r_put.status_code == 200, r_put.text
    assert c_j1.get("/api/v1/gurps/campanhas/sessoes/visiveis").json() == []

    r_del = c_m.delete(f"/api/v1/gurps/campanhas/sessoes/{sid}")
    assert r_del.status_code == 204


def test_admin_ve_todas_campanhas_e_sessoes(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre1, j1, _ = gurps_mestre_e_jogadores_db
    db = SessionLocal()
    try:
        mestre2 = Usuario(
            perfil=PerfilUsuario.MESTRE,
            nome="GURPS Mestre 2",
            email="gurps_mestre2_sess@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        admin = Usuario(
            perfil=PerfilUsuario.ADMINISTRADOR,
            nome="GURPS Admin",
            email="gurps_admin_sess@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add_all([mestre2, admin])
        db.commit()
        db.refresh(mestre2)
        db.refresh(admin)
    finally:
        db.close()

    c_j = _client(SessionLocal, _usuario(j1))
    c_m1 = _client(SessionLocal, _usuario(mestre1))
    c_m2 = _client(SessionLocal, _usuario(mestre2))
    c_adm = _client(SessionLocal, _usuario(admin))

    p = _criar_personagem(c_j, "Para duas mesas")
    id_c1 = c_m1.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Mesa M1", "personagem_ids": [p]},
    ).json()["id"]
    id_c2 = c_m2.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Mesa M2", "personagem_ids": []},
    ).json()["id"]

    c_m1.post(
        "/api/v1/gurps/campanhas/sessoes",
        json={"campanha_id": id_c1, "resumo": "S1", "visivel_jogadores": False},
    )
    c_m2.post(
        "/api/v1/gurps/campanhas/sessoes",
        json={"campanha_id": id_c2, "resumo": "S2", "visivel_jogadores": True},
    )

    campanhas = c_adm.get("/api/v1/gurps/campanhas").json()
    ids_c = {c["id"] for c in campanhas}
    assert id_c1 in ids_c and id_c2 in ids_c

    sessoes = c_adm.get("/api/v1/gurps/campanhas/sessoes").json()
    resumos = {s["resumo"] for s in sessoes}
    assert resumos >= {"S1", "S2"}

    r_up = c_adm.put(
        f"/api/v1/gurps/campanhas/{id_c2}",
        json={"descricao": "Admin editou"},
    )
    assert r_up.status_code == 200
    assert r_up.json()["descricao"] == "Admin editou"


def test_deletar_campanha_remove_sessoes_em_cascade(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    c_m = _client(SessionLocal, _usuario(mestre))
    c_j1 = _client(SessionLocal, _usuario(j1))
    p1 = _criar_personagem(c_j1, "P")
    cid = c_m.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Curta", "personagem_ids": [p1]},
    ).json()["id"]
    c_m.post(
        "/api/v1/gurps/campanhas/sessoes",
        json={"campanha_id": cid, "resumo": "Uma sessão", "visivel_jogadores": True},
    )
    assert c_m.delete(f"/api/v1/gurps/campanhas/{cid}").status_code == 204
    assert c_m.get("/api/v1/gurps/campanhas/sessoes").json() == []
