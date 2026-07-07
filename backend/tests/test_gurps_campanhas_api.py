"""Integração HTTP — campanhas GURPS (mestre/admin, personagens vinculados)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
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


def _client_campanhas(SessionLocal, usuario: SimpleNamespace) -> TestClient:
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


def test_jogador_lista_campanhas_vazias(gurps_mestre_e_jogadores_db):
    SessionLocal, _, j1, _ = gurps_mestre_e_jogadores_db
    client = _client_campanhas(SessionLocal, _usuario(j1))
    r = client.get("/api/v1/gurps/campanhas")
    assert r.status_code == 200
    assert r.json() == []


def test_jogador_cria_campanha(gurps_mestre_e_jogadores_db):
    SessionLocal, _, j1, _ = gurps_mestre_e_jogadores_db
    c_jog = _client_campanhas(SessionLocal, _usuario(j1))
    p1 = _criar_personagem(c_jog, "Herói solo")
    r = c_jog.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Minha mesa", "personagem_ids": [p1]},
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["nome"] == "Minha mesa"
    assert body["mestre_id"] == j1.id
    lst = c_jog.get("/api/v1/gurps/campanhas")
    assert lst.status_code == 200
    assert any(c["id"] == body["id"] for c in lst.json())


def test_mestre_cria_e_lista_campanha_com_personagens(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    c_jog = _client_campanhas(SessionLocal, _usuario(j1))
    c_mestre = _client_campanhas(SessionLocal, _usuario(mestre))

    p1 = _criar_personagem(c_jog, "Herói")
    p2 = _criar_personagem(c_jog, "Aliado")

    r = c_mestre.post(
        "/api/v1/gurps/campanhas",
        json={
            "nome": "Arco Felga",
            "descricao": "Teste integração",
            "personagem_ids": [p1, p2],
        },
    )
    assert r.status_code == 201, r.text
    body = r.json()
    cid = body["id"]
    assert body["nome"] == "Arco Felga"
    assert set(body["personagem_ids"]) == {p1, p2}
    assert body["total_personagens"] == 2

    lst = c_mestre.get("/api/v1/gurps/campanhas")
    assert lst.status_code == 200
    assert len(lst.json()) >= 1
    assert any(c["id"] == cid for c in lst.json())

    det = c_jog.get(f"/api/v1/gurps/personagens/{p1}")
    assert det.json()["campanha_id"] == cid


def test_mestre_put_substitui_personagens_da_campanha(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    c_jog = _client_campanhas(SessionLocal, _usuario(j1))
    c_mestre = _client_campanhas(SessionLocal, _usuario(mestre))

    p1 = _criar_personagem(c_jog, "A")
    p2 = _criar_personagem(c_jog, "B")
    r0 = c_mestre.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Mesa", "personagem_ids": [p1, p2]},
    )
    cid = r0.json()["id"]

    r = c_mestre.put(
        f"/api/v1/gurps/campanhas/{cid}",
        json={"personagem_ids": [p2]},
    )
    assert r.status_code == 200
    assert r.json()["personagem_ids"] == [p2]

    assert c_jog.get(f"/api/v1/gurps/personagens/{p1}").json()["campanha_id"] is None
    assert c_jog.get(f"/api/v1/gurps/personagens/{p2}").json()["campanha_id"] == cid


def test_mestre_post_personagens_adiciona_sem_remover_existentes(
    gurps_mestre_e_jogadores_db,
):
    """POST /personagens só associa os ids enviados; mantém os já na campanha."""
    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    c_jog = _client_campanhas(SessionLocal, _usuario(j1))
    c_mestre = _client_campanhas(SessionLocal, _usuario(mestre))

    p1 = _criar_personagem(c_jog, "Um")
    p2 = _criar_personagem(c_jog, "Dois")
    p3 = _criar_personagem(c_jog, "Tres")
    r0 = c_mestre.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Mesa add", "personagem_ids": [p1]},
    )
    assert r0.status_code == 201, r0.text
    cid = r0.json()["id"]

    r = c_mestre.post(
        f"/api/v1/gurps/campanhas/{cid}/personagens",
        json={"personagem_ids": [p2, p3]},
    )
    assert r.status_code == 200, r.text
    ids = set(r.json()["personagem_ids"])
    assert ids == {p1, p2, p3}


def test_mestre_delete_campanha_libera_personagens(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    c_jog = _client_campanhas(SessionLocal, _usuario(j1))
    c_mestre = _client_campanhas(SessionLocal, _usuario(mestre))

    p1 = _criar_personagem(c_jog, "Só eu")
    r0 = c_mestre.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Curta", "personagem_ids": [p1]},
    )
    cid = r0.json()["id"]

    r = c_mestre.delete(f"/api/v1/gurps/campanhas/{cid}")
    assert r.status_code == 204

    assert c_jog.get(f"/api/v1/gurps/personagens/{p1}").json()["campanha_id"] is None


def test_mestre_cria_com_personagem_inexistente_404(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre, _, _ = gurps_mestre_e_jogadores_db
    c_mestre = _client_campanhas(SessionLocal, _usuario(mestre))

    r = c_mestre.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Erro", "personagem_ids": [999999]},
    )
    assert r.status_code == 404


def test_mestre_nao_altera_campanha_de_outro(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    db = SessionLocal()
    try:
        m2 = Usuario(
            perfil=PerfilUsuario.MESTRE,
            nome="Outro M",
            email="gurps_mestre2@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add(m2)
        db.commit()
        db.refresh(m2)
        m2_ns = _usuario(m2)
    finally:
        db.close()

    c_m1 = _client_campanhas(SessionLocal, _usuario(mestre))
    c_j = _client_campanhas(SessionLocal, _usuario(j1))
    c_m2 = _client_campanhas(SessionLocal, m2_ns)

    p = _criar_personagem(c_j, "Npc alvo")
    r0 = c_m1.post(
        "/api/v1/gurps/campanhas",
        json={"nome": "Do M1", "personagem_ids": [p]},
    )
    cid = r0.json()["id"]

    r_forbidden = c_m2.put(
        f"/api/v1/gurps/campanhas/{cid}",
        json={"nome": "Invadir"},
    )
    assert r_forbidden.status_code == 404


def test_solicitacao_entrada_campanha_aceite_pelo_mestre(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    c_mestre = _client_campanhas(SessionLocal, _usuario(mestre))
    c_jog = _client_campanhas(SessionLocal, _usuario(j1))

    p1 = _criar_personagem(c_jog, "Herói Sol GURPS")
    cid = c_mestre.post(
        "/api/v1/gurps/campanhas", json={"nome": "Mesa Solicitacao GURPS"}
    ).json()["id"]

    r_sol = c_jog.post(
        "/api/v1/gurps/campanhas/solicitacoes",
        json={"campanha_id": cid, "personagem_id": p1},
    )
    assert r_sol.status_code == 201, r_sol.text
    sid = r_sol.json()["id"]

    r_pend = c_mestre.get("/api/v1/gurps/campanhas/solicitacoes/pendentes")
    assert any(x["id"] == sid for x in r_pend.json())

    r_ok = c_mestre.post(f"/api/v1/gurps/campanhas/solicitacoes/{sid}/aceitar")
    assert r_ok.status_code == 200

    r_p = c_jog.get(f"/api/v1/gurps/personagens/{p1}")
    assert r_p.json()["campanha_id"] == cid


def test_listar_disponiveis_retorna_campanhas(gurps_mestre_e_jogadores_db):
    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    c_mestre = _client_campanhas(SessionLocal, _usuario(mestre))
    c_jog = _client_campanhas(SessionLocal, _usuario(j1))
    c_mestre.post("/api/v1/gurps/campanhas", json={"nome": "Camp Publica GURPS"})
    r = c_jog.get("/api/v1/gurps/campanhas/disponiveis")
    assert r.status_code == 200
    assert "Camp Publica GURPS" in {c["nome"] for c in r.json()}
