"""Integração HTTP — combate GURPS (iniciar, turno, finalizar, RBAC em lote)."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.gurps.api.v1.combate import router as gurps_combate_router
from app.games.gurps.api.v1.personagens import router as gurps_personagens_router
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario


def _usuario(u: Usuario) -> SimpleNamespace:
    return SimpleNamespace(id=u.id, perfil=u.perfil, email=u.email, nome=u.nome)


def _build_client(SessionLocal, usuario: SimpleNamespace) -> TestClient:
    app = FastAPI()
    app.include_router(gurps_personagens_router, prefix="/api/v1")
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


def _criar(session_local, client: TestClient, nome: str, iniciativa: int) -> int:
    r = client.post(
        "/api/v1/gurps/personagens",
        json={
            "nome": nome,
            "tipo": "jogador",
            "iniciativa": iniciativa,
            "extras": {},
        },
    )
    assert r.status_code == 201, r.text
    return r.json()["id"]


def test_iniciar_ordena_por_iniciativa_desc(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    p_baixa = _criar(SessionLocal, client, "Lento", 3)
    p_alta = _criar(SessionLocal, client, "Rápido", 12)

    r = client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [p_baixa, p_alta]},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["ativo"] is True
    assert body["personagens_ids"] == [p_alta, p_baixa]
    assert body["turno_atual"] == 0
    assert body["personagem_ativo_id"] == p_alta


def test_iniciar_duas_vezes_retorna_400(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "A", 5)
    b = _criar(SessionLocal, client, "B", 4)

    assert client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [a, b]},
    ).status_code == 200

    r2 = client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [a]},
    )
    assert r2.status_code == 400
    assert "combate" in r2.json().get("detail", "").lower()


def test_finalizar_e_status_inativo(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "Só", 1)
    assert client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [a]},
    ).status_code == 200

    r = client.post("/api/v1/gurps/combate/finalizar")
    assert r.status_code == 200
    assert r.json().get("ativo") is False

    st = client.get("/api/v1/gurps/combate/status")
    assert st.status_code == 200
    assert st.json().get("ativo") is False


def test_avancar_volta_ao_inicio_incrementa_rodada(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "P1", 10)
    b = _criar(SessionLocal, client, "P2", 9)
    assert client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [a, b]},
    ).status_code == 200

    assert client.post("/api/v1/gurps/combate/avancar-turno").json()["turno_atual"] == 1
    r2 = client.post("/api/v1/gurps/combate/avancar-turno")
    assert r2.status_code == 200
    body = r2.json()
    assert body["turno_atual"] == 0
    assert body["rodada_atual"] == 2


def test_avancar_turno_incrementa(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    a = _criar(SessionLocal, client, "P1", 10)
    b = _criar(SessionLocal, client, "P2", 9)
    assert client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [a, b]},
    ).status_code == 200

    r = client.post("/api/v1/gurps/combate/avancar-turno")
    assert r.status_code == 200
    assert r.json()["turno_atual"] == 1
    assert r.json()["personagem_ativo_id"] == b


def test_avancar_sem_combate_404(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post("/api/v1/gurps/combate/avancar-turno")
    assert r.status_code == 404


def test_iniciar_com_id_inexistente_404(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post(
        "/api/v1/gurps/combate/iniciar",
        json={"personagem_ids": [999999]},
    )
    assert r.status_code == 404


def test_iniciar_com_personagem_de_outro_dono_403(gurps_personagens_db):
    SessionLocal, u1, u2 = gurps_personagens_db
    c1 = _build_client(SessionLocal, _usuario(u1))
    pid = _criar(SessionLocal, c1, "Dono1", 7)

    c2 = _build_client(SessionLocal, _usuario(u2))
    r = c2.post("/api/v1/gurps/combate/iniciar", json={"personagem_ids": [pid]})
    assert r.status_code == 403
