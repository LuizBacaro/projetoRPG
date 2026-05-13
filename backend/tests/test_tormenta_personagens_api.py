"""Integração HTTP — personagens Tormenta (CRUD básico)."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.dependencies import get_file_service
from app.games.tormenta.api.v1.personagens import router as tormenta_personagens_router
from app.services.file_service import FileService
from app.shared.core.database import get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import Usuario


@pytest.fixture(scope="function")
def tormenta_personagens_db():
    """SQLite em memória: dois jogadores + um mestre (monstro sem validação de compra)."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    import app.models  # noqa: F401
    from app.shared.core.database import Base
    from app.shared.core.security import hash_senha
    from app.shared.models.usuario import PerfilUsuario, Usuario as UModel

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        u1 = UModel(
            perfil=PerfilUsuario.JOGADOR,
            nome="Tormenta Um",
            email="tormenta1@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        u2 = UModel(
            perfil=PerfilUsuario.JOGADOR,
            nome="Tormenta Dois",
            email="tormenta2@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        u_mestre = UModel(
            perfil=PerfilUsuario.MESTRE,
            nome="Tormenta Mestre",
            email="tormenta.mestre@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add_all([u1, u2, u_mestre])
        db.commit()
        db.refresh(u1)
        db.refresh(u2)
        db.refresh(u_mestre)
        yield SessionLocal, u1, u2, u_mestre
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _build_client(SessionLocal, usuario: SimpleNamespace, file_service=None) -> TestClient:
    app = FastAPI()
    app.include_router(tormenta_personagens_router, prefix="/api/v1")

    def _override_get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario
    if file_service is not None:
        app.dependency_overrides[get_file_service] = lambda: file_service
    return TestClient(app)


def _usuario(u: Usuario) -> SimpleNamespace:
    return SimpleNamespace(id=u.id, perfil=u.perfil, email=u.email, nome=u.nome)


def test_criar_e_listar(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json={
            "nome": "Arthas",
            "tipo": "jogador",
            "classe_nivel": "Guerreiro 3",
            "ficha_json": {"pericias": [{"nome": "Luta", "graduacao": 2, "outros": 0, "somente_treinado": False}]},
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["nome"] == "Arthas"
    assert body["ficha_json"]["pericias"][0]["nome"] == "Luta"

    r2 = client.get("/api/v1/tormenta/personagens")
    assert r2.status_code == 200
    assert len(r2.json()) >= 1


def test_post_foto_atualiza_foto_url(tormenta_personagens_db, monkeypatch, tmp_path):
    SessionLocal, u1, *_ = tormenta_personagens_db
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_CLOUD_NAME", "")
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_API_KEY", "")
    monkeypatch.setattr("app.services.file_service.settings.CLOUDINARY_API_SECRET", "")
    monkeypatch.setattr("app.services.file_service.settings.UPLOADS_DIR", tmp_path)
    monkeypatch.setattr("app.services.file_service.settings.MAX_FILE_SIZE", 1024 * 1024)
    monkeypatch.setattr(
        "app.services.file_service.settings.ALLOWED_EXTENSIONS", {".png"}
    )
    client = _build_client(SessionLocal, _usuario(u1), FileService())
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json={"nome": "ComFoto", "tipo": "jogador"},
    ).json()["id"]
    png = b"\x89PNG\r\n\x1a\n" + (b"\x00" * 32)
    r = client.post(
        f"/api/v1/tormenta/personagens/{rid}/foto",
        files={"foto": ("retrato.png", BytesIO(png), "image/png")},
    )
    assert r.status_code == 200, r.text
    url = r.json().get("foto_url")
    assert url
    assert "/uploads/" in url or url.startswith("http")
    r2 = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert r2.json()["foto_url"] == url
    assert (tmp_path / Path(url).name).is_file()


def test_patch_foto_url(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json={"nome": "ComFoto", "tipo": "jogador"},
    ).json()["id"]
    url = "https://example.com/retrato.png"
    r = client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"foto_url": url},
    )
    assert r.status_code == 200
    assert r.json()["foto_url"] == url
    r2 = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert r2.json()["foto_url"] == url


def test_patch_ficha_json(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json={"nome": "Beta", "tipo": "jogador"},
    ).json()["id"]
    r = client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={"ficha_json": {"notas": "teste"}},
    )
    assert r.status_code == 200
    assert r.json()["ficha_json"]["notas"] == "teste"


def test_delete(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json={"nome": "Gamma", "tipo": "jogador"},
    ).json()["id"]
    d = client.delete(f"/api/v1/tormenta/personagens/{rid}")
    assert d.status_code == 204
    g = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert g.status_code == 404


def test_criar_jogador_com_atributos_compra_excede_orcamento(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json={
            "nome": "Invalido",
            "tipo": "jogador",
            "for_valor": 10,
            "des_valor": 10,
            "con_valor": 10,
            "int_valor": 10,
            "sab_valor": 10,
            "car_valor": 10,
            "ficha_json": {
                "atributos_compra": {
                    "for": 18,
                    "des": 18,
                    "con": 18,
                    "int": 18,
                    "sab": 18,
                    "car": 18,
                }
            },
        },
    )
    assert r.status_code == 422
    d = r.json().get("detail", "").lower()
    assert "ultrapassar" in d or "20" in d


def test_criar_monstro_dez_em_todos_ok(tormenta_personagens_db):
    SessionLocal, _, _, u_mestre = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u_mestre))
    r = client.post(
        "/api/v1/tormenta/personagens",
        json={
            "nome": "Bicho",
            "tipo": "monstro",
            "for_valor": 10,
            "des_valor": 10,
            "con_valor": 10,
            "int_valor": 10,
            "sab_valor": 10,
            "car_valor": 10,
        },
    )
    assert r.status_code == 201
    assert r.json()["for_valor"] == 10


def test_patch_jogador_atributos_compra_ultrapassa_rejeita(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json={"nome": "Heroi", "tipo": "jogador"},
    ).json()["id"]
    r = client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={
            "ficha_json": {
                "atributos_compra": {
                    "for": 18,
                    "des": 18,
                    "con": 18,
                    "int": 18,
                    "sab": 18,
                    "car": 18,
                }
            }
        },
    )
    assert r.status_code == 422
    assert "ultrapassar" in r.json().get("detail", "").lower()


def test_talentos_crud_e_get_personagem_inclui_lista(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json={"nome": "ComTalentos", "tipo": "jogador"},
    ).json()["id"]
    nome_unico = "Talento Teste API Único XYZ"
    r_add = client.post(
        f"/api/v1/tormenta/personagens/{rid}/talentos",
        json={"nome": nome_unico},
    )
    assert r_add.status_code == 201, r_add.text
    body = r_add.json()
    assert body["nome"] == nome_unico
    vid = body["id"]

    r_dup = client.post(
        f"/api/v1/tormenta/personagens/{rid}/talentos",
        json={"nome": nome_unico},
    )
    assert r_dup.status_code == 409

    r_get = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert r_get.status_code == 200
    tlist = r_get.json().get("talentos") or []
    assert len(tlist) == 1
    assert tlist[0]["nome"] == nome_unico

    r_list = client.get(f"/api/v1/tormenta/personagens/{rid}/talentos")
    assert r_list.status_code == 200
    assert len(r_list.json()) == 1

    d = client.delete(f"/api/v1/tormenta/personagens/{rid}/talentos/{vid}")
    assert d.status_code == 204
    r_empty = client.get(f"/api/v1/tormenta/personagens/{rid}")
    assert (r_empty.json().get("talentos") or []) == []


def test_migrar_talentos_mb_lista_do_json(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json={"nome": "MigrarTal", "tipo": "jogador"},
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={
            "ficha_json": {
                "talentos_mb_lista": [
                    {"nome": "Talento Migra A"},
                    {"nome": "Talento Migra A"},
                    {"nome": "Talento Migra B"},
                ]
            }
        },
    )
    r = client.post(f"/api/v1/tormenta/personagens/{rid}/talentos/migrar-do-json")
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["vinculos_criados"] == 2
    assert data["ignorados_duplicados"] == 1
    names = {x["nome"] for x in client.get(f"/api/v1/tormenta/personagens/{rid}/talentos").json()}
    assert names == {"Talento Migra A", "Talento Migra B"}


def test_importar_inventario_legado_remove_json(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json={"nome": "Legado", "tipo": "jogador"},
    ).json()["id"]
    client.patch(
        f"/api/v1/tormenta/personagens/{rid}",
        json={
            "ficha_json": {
                "talentos_mb_lista": [{"nome": "Talento Único Legado"}],
                "equipamentos": [{"item": "Espada de Teste", "qtd": "2"}],
            }
        },
    )
    r = client.post(f"/api/v1/tormenta/personagens/{rid}/inventario/importar-legado")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["talentos_criados"] >= 1
    assert body["equipamentos_criados"] >= 1
    p = client.get(f"/api/v1/tormenta/personagens/{rid}").json()
    fj = p.get("ficha_json") or {}
    assert "talentos_mb_lista" not in fj
    assert "equipamentos" not in fj
    assert len(p.get("talentos") or []) >= 1
    assert len(p.get("equipamentos") or []) >= 1


def test_equipamentos_post_e_get(tormenta_personagens_db):
    SessionLocal, u1, *_ = tormenta_personagens_db
    client = _build_client(SessionLocal, _usuario(u1))
    rid = client.post(
        "/api/v1/tormenta/personagens",
        json={"nome": "Eq", "tipo": "jogador"},
    ).json()["id"]
    r = client.post(
        f"/api/v1/tormenta/personagens/{rid}/equipamentos",
        json={"nome": "Item API Equip Único", "quantidade": 3},
    )
    assert r.status_code == 201, r.text
    assert r.json()["quantidade"] == 3
    lst = client.get(f"/api/v1/tormenta/personagens/{rid}/equipamentos").json()
    assert len(lst) == 1
    vid = lst[0]["id"]
    p = client.patch(
        f"/api/v1/tormenta/personagens/{rid}/equipamentos/{vid}",
        json={"quantidade": 5},
    )
    assert p.status_code == 200
    assert p.json()["quantidade"] == 5
