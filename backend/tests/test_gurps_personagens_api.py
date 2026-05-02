"""Integração HTTP — personagens GURPS (extras, validação, RBAC básico)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.dependencies import get_file_service
from app.games.gurps.api.v1.personagens import router as gurps_personagens_router
from app.games.gurps.schemas.personagem import GURPS_EXTRAS_MAX_JSON_BYTES
from app.services.file_service import FileService
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario


def _build_client(SessionLocal, usuario: SimpleNamespace) -> TestClient:
    app = FastAPI()
    app.include_router(gurps_personagens_router, prefix="/api/v1")

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
        "nome": "Personagem Teste",
        "tipo": "jogador",
        "extras": {
            "criacao": "2026-05-01",
            "equipamento": "Ração",
            "hit": {"cranio": "3"},
            "enc": {"leve": {"fp": "1", "d": "0"}},
            "arma": {"golp": "sw", "bal": "thr", "nh": "12"},
        },
    }
    body.update(overrides)
    return body


def test_criar_personagem_persiste_extras_e_versao_v(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post("/api/v1/gurps/personagens", json=_payload_criar())
    assert r.status_code == 201, r.text
    data = r.json()
    assert data["id"] >= 1
    assert data["dono_id"] == u1.id
    ex = data["extras"]
    assert ex.get("v") == 1
    assert ex["hit"]["cranio"] == "3"
    assert ex["equipamento"] == "Ração"

    r2 = client.get(f"/api/v1/gurps/personagens/{data['id']}")
    assert r2.status_code == 200
    assert r2.json()["extras"]["hit"]["cranio"] == "3"


def test_patch_nome_nao_apaga_extras(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    c = client.post("/api/v1/gurps/personagens", json=_payload_criar(nome="Alpha"))
    pid = c.json()["id"]

    r = client.patch(f"/api/v1/gurps/personagens/{pid}", json={"nome": "Beta"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["nome"] == "Beta"
    assert body["extras"]["hit"]["cranio"] == "3"
    assert body["extras"].get("v") == 1


def test_patch_extras_substitui_objeto(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    c = client.post("/api/v1/gurps/personagens", json=_payload_criar())
    pid = c.json()["id"]

    r = client.patch(
        f"/api/v1/gurps/personagens/{pid}",
        json={"extras": {"nota": "só isso", "v": 1}},
    )
    assert r.status_code == 200, r.text
    ex = r.json()["extras"]
    assert ex["nota"] == "só isso"
    assert "hit" not in ex


def test_criar_sem_nome_rejeita(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post("/api/v1/gurps/personagens", json={"nome": "  ", "tipo": "jogador"})
    assert r.status_code in (400, 422)
    r2 = client.post("/api/v1/gurps/personagens", json={"tipo": "jogador"})
    assert r2.status_code == 422


def test_criar_rejeita_extras_maior_que_limite(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    huge = {"k": "x" * (GURPS_EXTRAS_MAX_JSON_BYTES + 100)}
    r = client.post("/api/v1/gurps/personagens", json=_payload_criar(extras=huge))
    assert r.status_code == 422
    det = r.json().get("detail", "")
    assert isinstance(det, list) or "extras" in str(det).lower() or "65536" in str(det)


def test_jogador_nao_acessa_personagem_de_outro(gurps_personagens_db):
    SessionLocal, u1, u2 = gurps_personagens_db
    c1 = _build_client(SessionLocal, _usuario(u1))
    c = c1.post("/api/v1/gurps/personagens", json=_payload_criar(nome="Do dono 1"))
    pid = c.json()["id"]

    c2 = _build_client(SessionLocal, _usuario(u2))
    r = c2.get(f"/api/v1/gurps/personagens/{pid}")
    assert r.status_code == 403


def test_post_foto_atualiza_foto_url(gurps_personagens_db, monkeypatch, tmp_path):
    SessionLocal, u1, _ = gurps_personagens_db
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_CLOUD_NAME", "")
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_API_KEY", "")
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_API_SECRET", "")
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024 * 1024)
    monkeypatch.setattr("app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"})

    app = FastAPI()
    app.include_router(gurps_personagens_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: _usuario(u1)
    app.dependency_overrides[get_file_service] = lambda: FileService()
    client = TestClient(app)

    c = client.post("/api/v1/gurps/personagens", json=_payload_criar(nome="Com Foto"))
    pid = c.json()["id"]

    png = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 32)
    r = client.post(
        f"/api/v1/gurps/personagens/{pid}/foto",
        files={"foto": ("retrato.png", BytesIO(png), "image/png")},
    )
    assert r.status_code == 200, r.text
    url = r.json().get("foto_url")
    assert url
    assert "/uploads/" in url or url.startswith("http")

    r2 = client.get(f"/api/v1/gurps/personagens/{pid}")
    assert r2.json()["foto_url"] == url


def test_post_segunda_foto_remove_arquivo_anterior(gurps_personagens_db, monkeypatch, tmp_path):
    SessionLocal, u1, _ = gurps_personagens_db
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_CLOUD_NAME", "")
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_API_KEY", "")
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_API_SECRET", "")
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024 * 1024)
    monkeypatch.setattr("app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"})

    app = FastAPI()
    app.include_router(gurps_personagens_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: _usuario(u1)
    app.dependency_overrides[get_file_service] = lambda: FileService()
    client = TestClient(app)

    pid = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="Duas fotos"),
    ).json()["id"]

    png = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 32)
    r1 = client.post(
        f"/api/v1/gurps/personagens/{pid}/foto",
        files={"foto": ("primeira.png", BytesIO(png), "image/png")},
    )
    assert r1.status_code == 200
    url1 = r1.json()["foto_url"]
    nome1 = Path(url1).name
    assert (tmp_path / nome1).is_file()

    r2 = client.post(
        f"/api/v1/gurps/personagens/{pid}/foto",
        files={"foto": ("segunda.png", BytesIO(png), "image/png")},
    )
    assert r2.status_code == 200
    url2 = r2.json()["foto_url"]
    assert url2 != url1
    assert not (tmp_path / nome1).exists(), "arquivo antigo deveria ter sido apagado"
    assert (tmp_path / Path(url2).name).is_file()


def test_jogador_lista_apenas_próprios(gurps_personagens_db):
    SessionLocal, u1, u2 = gurps_personagens_db
    c1 = _build_client(SessionLocal, _usuario(u1))
    c2 = _build_client(SessionLocal, _usuario(u2))

    assert c1.post("/api/v1/gurps/personagens", json=_payload_criar(nome="P1")).status_code == 201
    assert c2.post("/api/v1/gurps/personagens", json=_payload_criar(nome="P2")).status_code == 201

    r1 = c1.get("/api/v1/gurps/personagens")
    assert r1.status_code == 200
    nomes1 = {p["nome"] for p in r1.json()}
    assert "P1" in nomes1
    assert "P2" not in nomes1

    r2 = c2.get("/api/v1/gurps/personagens")
    assert r2.status_code == 200
    nomes2 = {p["nome"] for p in r2.json()}
    assert "P2" in nomes2
    assert "P1" not in nomes2
