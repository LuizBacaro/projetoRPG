"""Fluxo mesa — campanha (mestre) + combate com personagens dos jogadores."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.gurps.api.v1.campanhas import router as gurps_campanhas_router
from app.games.gurps.api.v1.combate import router as gurps_combate_router
from app.games.gurps.api.v1.personagens import router as gurps_personagens_router
from app.shared.constants import GAME_SLUG_GURPS
from app.shared.core.config import settings
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.core.security import criar_token
from app.shared.models.usuario import Usuario


def _usuario(u: Usuario) -> SimpleNamespace:
    return SimpleNamespace(id=u.id, perfil=u.perfil, email=u.email, nome=u.nome)


def _client_mesa(SessionLocal, usuario: SimpleNamespace) -> TestClient:
    app = FastAPI()
    app.include_router(gurps_personagens_router, prefix="/api/v1")
    app.include_router(gurps_campanhas_router, prefix="/api/v1")
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


def _app_mesa_jwt_auth(SessionLocal):
    app = FastAPI()
    app.include_router(gurps_personagens_router, prefix="/api/v1")
    app.include_router(gurps_campanhas_router, prefix="/api/v1")
    app.include_router(gurps_combate_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    return app


def _criar_personagem(client: TestClient, nome: str, iniciativa: int = 0) -> int:
    r = client.post(
        "/api/v1/gurps/personagens",
        json={"nome": nome, "tipo": "jogador", "iniciativa": iniciativa, "extras": {}},
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_mestre_cria_campanha_e_inicia_combate_com_personagens_do_jogador(
    gurps_mestre_e_jogadores_db,
):
    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    c_jog = _client_mesa(SessionLocal, _usuario(j1))
    c_mestre = _client_mesa(SessionLocal, _usuario(mestre))

    p_lento = _criar_personagem(c_jog, "Escudeiro", iniciativa=5)
    p_rapido = _criar_personagem(c_jog, "Cavaleiro", iniciativa=12)

    r_camp = c_mestre.post(
        "/api/v1/gurps/campanhas",
        json={
            "nome": "Noite na taverna",
            "descricao": "fluxo integração",
            "personagem_ids": [p_lento, p_rapido],
        },
    )
    assert r_camp.status_code == 201, r_camp.text
    cid = r_camp.json()["id"]
    assert set(r_camp.json()["personagem_ids"]) == {p_lento, p_rapido}

    assert c_jog.get(f"/api/v1/gurps/personagens/{p_rapido}").json()["campanha_id"] == cid

    r_comb = c_mestre.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [p_lento, p_rapido]},
    )
    assert r_comb.status_code == 200, r_comb.text
    body = r_comb.json()
    assert body["ativo"] is True
    assert body["personagens_ids"] == [p_rapido, p_lento]
    assert body["personagem_ativo_id"] == p_rapido

    assert c_mestre.post("/api/v1/gurps/combate/finalizar").status_code == 200


def test_fluxo_mesa_multijogo_estrito_token_gurps(gurps_mestre_e_jogadores_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, mestre, j1, _ = gurps_mestre_e_jogadores_db
    client = TestClient(_app_mesa_jwt_auth(SessionLocal))

    tok_j = criar_token(
        data={"sub": j1.email, "game_slug": GAME_SLUG_GURPS},
        secret_key=settings.SECRET_KEY,
    )
    tok_m = criar_token(
        data={"sub": mestre.email, "game_slug": GAME_SLUG_GURPS},
        secret_key=settings.SECRET_KEY,
    )
    h_j = {"Authorization": f"Bearer {tok_j}"}
    h_m = {"Authorization": f"Bearer {tok_m}"}

    r0 = client.post(
        "/api/v1/gurps/personagens",
        headers=h_j,
        json={"nome": "PJ Strict", "tipo": "jogador", "iniciativa": 7, "extras": {}},
    )
    assert r0.status_code == 201, r0.text
    p1 = r0.json()["id"]

    r_c = client.post(
        "/api/v1/gurps/campanhas",
        headers=h_m,
        json={"nome": "Mesa strict JWT", "personagem_ids": [p1]},
    )
    assert r_c.status_code == 201, r_c.text
    assert r_c.json()["id"] >= 1
    assert p1 in r_c.json()["personagem_ids"]

    r_i = client.post(
        "/api/v1/gurps/combate/iniciar",
        headers=h_m,
        json={"personagem_ids": [p1]},
    )
    assert r_i.status_code == 200, r_i.text
    assert r_i.json()["personagens_ids"] == [p1]

    assert client.post("/api/v1/gurps/combate/finalizar", headers=h_m).status_code == 200


def test_fluxo_mesa_estrito_sem_slug_bloqueia_criacao_personagem(gurps_mestre_e_jogadores_db, monkeypatch):
    monkeypatch.setattr(settings, "MULTI_GAME_STRICT_MODE", True)

    SessionLocal, _, j1, _ = gurps_mestre_e_jogadores_db
    client = TestClient(_app_mesa_jwt_auth(SessionLocal))

    tok = criar_token(data={"sub": j1.email}, secret_key=settings.SECRET_KEY)
    r = client.post(
        "/api/v1/gurps/personagens",
        headers={"Authorization": f"Bearer {tok}"},
        json={"nome": "Sem slug", "tipo": "jogador", "extras": {}},
    )
    assert r.status_code == 409
