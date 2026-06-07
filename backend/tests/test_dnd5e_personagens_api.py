"""Integração HTTP — personagens D&D 5e."""

from __future__ import annotations

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd5e.api.v1.personagens import router as dnd5e_personagens_router
from app.games.dnd5e.schemas.personagem import DND5E_FICHA_MAX_JSON_BYTES
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario


def _build_client(SessionLocal, usuario: SimpleNamespace) -> TestClient:
    app = FastAPI()
    app.include_router(dnd5e_personagens_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    return TestClient(app)


def _usuario(u: Usuario) -> SimpleNamespace:
    return SimpleNamespace(id=u.id, perfil=u.perfil, email=u.email, nome=u.nome)


def _payload_criar(**overrides):
    body = {
        "nome": "Aragorn 5e",
        "tipo": "jogador",
        "nivel": 5,
        "experiencia": 6500,
        "strength": 16,
        "dexterity": 14,
        "constitution": 14,
        "ficha": {"raca": "humano", "classe": "guerreiro"},
    }
    body.update(overrides)
    return body


def test_criar_personagem_com_modificadores_calculados(dnd5e_personagens_db):
    SessionLocal, u1, _ = dnd5e_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post("/api/v1/dnd5e/personagens", json=_payload_criar())
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == "Aragorn 5e"
    assert body["strength_mod"] == 3
    assert body["dexterity_mod"] == 2
    assert body["bonus_proficiencia"] == 3
    assert body["ficha"]["raca"] == "humano"
    assert body["ficha"].get("v") == 2
    assert body["dono_id"] == u1.id


def test_patch_nome_nao_apaga_ficha(dnd5e_personagens_db):
    SessionLocal, u1, _ = dnd5e_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    created = client.post("/api/v1/dnd5e/personagens", json=_payload_criar()).json()
    pid = created["id"]

    r = client.patch(f"/api/v1/dnd5e/personagens/{pid}", json={"nome": "Renomeado"})
    assert r.status_code == 200
    assert r.json()["nome"] == "Renomeado"
    assert r.json()["ficha"]["classe"] == "guerreiro"


def test_criar_sem_nome_rejeita(dnd5e_personagens_db):
    SessionLocal, u1, _ = dnd5e_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post("/api/v1/dnd5e/personagens", json=_payload_criar(nome="  "))
    assert r.status_code in (400, 422)


def test_criar_habilidade_invalida_rejeita(dnd5e_personagens_db):
    SessionLocal, u1, _ = dnd5e_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post("/api/v1/dnd5e/personagens", json=_payload_criar(strength=0))
    assert r.status_code == 422


def test_jogador_nao_acessa_personagem_de_outro(dnd5e_personagens_db):
    SessionLocal, u1, u2 = dnd5e_personagens_db
    client1 = _build_client(SessionLocal, _usuario(u1))
    client2 = _build_client(SessionLocal, _usuario(u2))
    pid = client1.post("/api/v1/dnd5e/personagens", json=_payload_criar()).json()["id"]

    r = client2.get(f"/api/v1/dnd5e/personagens/{pid}")
    assert r.status_code == 403


def test_jogador_lista_apenas_proprios(dnd5e_personagens_db):
    SessionLocal, u1, u2 = dnd5e_personagens_db
    client1 = _build_client(SessionLocal, _usuario(u1))
    client2 = _build_client(SessionLocal, _usuario(u2))
    client1.post("/api/v1/dnd5e/personagens", json=_payload_criar(nome="A"))
    client2.post("/api/v1/dnd5e/personagens", json=_payload_criar(nome="B"))

    r = client1.get("/api/v1/dnd5e/personagens")
    assert r.status_code == 200
    nomes = {p["nome"] for p in r.json()}
    assert nomes == {"A"}


def test_criar_ficha_phb_sem_pericias_rejeita(dnd5e_personagens_db):
    SessionLocal, u1, _ = dnd5e_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    base = {
        k: 10
        for k in (
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        )
    }
    r = client.post(
        "/api/v1/dnd5e/personagens",
        json=_payload_criar(
            nivel=1,
            ficha={
                "raca_slug": "elfo",
                "classe_slug": "ladino",
                "scores_base": base,
                "pericias_classe_escolhidas": ["furtividade"],
            },
        ),
    )
    assert r.status_code in (400, 422)


def test_criar_rejeita_ficha_maior_que_limite(dnd5e_personagens_db):
    SessionLocal, u1, _ = dnd5e_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    blob = {"x": "a" * DND5E_FICHA_MAX_JSON_BYTES}
    r = client.post("/api/v1/dnd5e/personagens", json=_payload_criar(ficha=blob))
    assert r.status_code == 422


def test_excluir_personagem(dnd5e_personagens_db):
    SessionLocal, u1, _ = dnd5e_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    created = client.post("/api/v1/dnd5e/personagens", json=_payload_criar()).json()
    pid = created["id"]

    r = client.delete(f"/api/v1/dnd5e/personagens/{pid}")
    assert r.status_code == 204
    assert client.get(f"/api/v1/dnd5e/personagens/{pid}").status_code == 404
