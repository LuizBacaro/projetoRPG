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
from app.games.gurps.catalogs.lite_catalog import montar_catalogo_de_arquivos
from app.games.gurps.repositories.catalogo_ficha_repository import repopular_catalogo_ficha_de_arquivos
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


def test_listar_aceita_limit_500_para_campanhas_e_dashboard(gurps_personagens_db):
    """UI de campanhas pede limit=500; acima do teto antigo (200) gerava 422."""
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.get("/api/v1/gurps/personagens", params={"limit": 500})
    assert r.status_code == 200, r.text


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


def test_criar_calcula_vb_e_deslocamento_quando_omitidos(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="Calc", dx_valor=12, ht_valor=10),
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert float(body["velocidade_valor"]) == pytest.approx(5.5)
    assert body["deslocamento_valor"] == 5


def test_patch_ht_dx_recalcula_vb_e_deslocamento_quando_nao_override(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    pid = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="Recalc", dx_valor=10, ht_valor=10),
    ).json()["id"]

    r = client.patch(
        f"/api/v1/gurps/personagens/{pid}",
        json={"dx_valor": 14, "ht_valor": 10},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert float(body["velocidade_valor"]) == pytest.approx(6.0)
    assert body["deslocamento_valor"] == 6


def test_criar_default_pv_fad_por_st_ht_quando_omitidos(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="PVFAD", st_valor=12, ht_valor=11),
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["pvs_valor"] == 12
    assert body["fadiga_valor"] == 11
    assert body["pvs_atual"] == 12
    assert body["fadiga_atual"] == 11


def test_patch_st_ht_recalcula_maximos_sem_override(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    pid = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="RecalcPVFAD", st_valor=10, ht_valor=10),
    ).json()["id"]

    client.patch(
        f"/api/v1/gurps/personagens/{pid}",
        json={"pvs_atual": 6, "fadiga_atual": 5},
    )
    r = client.patch(f"/api/v1/gurps/personagens/{pid}", json={"st_valor": 8, "ht_valor": 9})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["pvs_valor"] == 8
    assert body["fadiga_valor"] == 9
    assert body["pvs_atual"] == 6
    assert body["fadiga_atual"] == 5


def test_criar_default_von_per_por_iq_quando_omitidos(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="VonPer", iq_valor=13),
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["vontade_valor"] == 13
    assert body["percepcao_valor"] == 13


def test_patch_iq_recalcula_von_per_sem_override(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    pid = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="RecalcIQ", iq_valor=10),
    ).json()["id"]

    r = client.patch(f"/api/v1/gurps/personagens/{pid}", json={"iq_valor": 14})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["vontade_valor"] == 14
    assert body["percepcao_valor"] == 14


def test_criar_default_esquiva_por_vb_quando_omitida(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="EsquivaDefault", velocidade_valor=6.75),
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["esquiva"] == 9  # floor(6.75) + 3


def test_patch_vb_recalcula_esquiva_sem_override(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    pid = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="EsquivaRecalc", velocidade_valor=5.0),
    ).json()["id"]

    r = client.patch(f"/api/v1/gurps/personagens/{pid}", json={"velocidade_valor": 7.25})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["esquiva"] == 10  # floor(7.25) + 3


def test_criar_default_dano_por_st_quando_omitido(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="DanoST", st_valor=13),
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert body["dano_impacto"] == "1d"
    assert body["dano_balanco"] == "2d-1"


def test_patch_st_recalcula_dano_sem_override(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    pid = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(nome="DanoRecalc", st_valor=10),
    ).json()["id"]

    r = client.patch(f"/api/v1/gurps/personagens/{pid}", json={"st_valor": 15})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["dano_impacto"] == "1d+1"
    assert body["dano_balanco"] == "2d+1"


def test_catalogo_pericias_lite_disponivel(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.get("/api/v1/gurps/personagens/catalogo/pericias-lite")
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body.get("itens"), list)
    nomes = {x.get("nome") for x in body["itens"]}
    assert "Briga" in nomes
    assert "Medicina" in nomes


def test_catalogo_lite_ficha_retorna_pericias_vantagens_desvantagens(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.get("/api/v1/gurps/personagens/catalogo/lite-ficha")
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body.get("pericias"), list) and len(body["pericias"]) >= 50
    assert isinstance(body.get("vantagens"), list) and len(body["vantagens"]) >= 50
    assert isinstance(body.get("desvantagens"), list) and len(body["desvantagens"]) >= 50
    assert body["pericias"][0].get("nome")
    assert "meta" in body and "custos_atributos" in body["meta"]
    assert "custos_pontos_fonte" in body["meta"]
    assert "fonte_listas_personagens_pdf" in body["meta"]


def test_catalogo_lite_ficha_via_banco_apos_seed(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    esperado = montar_catalogo_de_arquivos()
    db = SessionLocal()
    try:
        repopular_catalogo_ficha_de_arquivos(db)
        db.commit()
    finally:
        db.close()

    client = _build_client(SessionLocal, _usuario(u1))
    r = client.get("/api/v1/gurps/personagens/catalogo/lite-ficha")
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["pericias"]) == len(esperado["pericias"])
    assert {p["nome"] for p in body["pericias"]} == {p["nome"] for p in esperado["pericias"]}
    assert len(body["vantagens"]) == len(esperado["vantagens"])
    assert len(body["desvantagens"]) == len(esperado["desvantagens"])
    assert "custos_atributos" in body["meta"]
    assert "fonte_listas_personagens_pdf" in body["meta"]


def test_criar_rejeita_pericia_lite_sem_pre_requisito(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(
            nome="Sem prereq",
            iq_valor=10,
            pericias=[{"nome": "Medicina", "tipo": "D", "nh": 10, "custo": 1}],
        ),
    )
    assert r.status_code in (400, 422), r.text
    assert "medicina" in str(r.json().get("detail", "")).lower()


def test_criar_aceita_pericia_lite_com_pre_requisito(gurps_personagens_db):
    SessionLocal, u1, _ = gurps_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))

    r = client.post(
        "/api/v1/gurps/personagens",
        json=_payload_criar(
            nome="Com prereq",
            iq_valor=12,
            pericias=[{"nome": "Medicina", "tipo": "D", "nh": 12, "custo": 2}],
        ),
    )
    assert r.status_code == 201, r.text
    body = r.json()
    assert any(p["nome"] == "Medicina" for p in body.get("pericias", []))
