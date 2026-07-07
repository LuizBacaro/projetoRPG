"""Testes do endpoint /api/v1/divindades/custom (divindades de campanha)."""

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.games.dnd35.api.v1.divindades_custom import router as divindades_router
from app.games.dnd35.api.v1.magias import router as magias_router
from app.shared.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual, requer_mestre_dnd35_ou_admin
from app.shared.models.usuario import PerfilUsuario


class _UsuarioDummy:
    def __init__(self, user_id: int = 77, perfil: PerfilUsuario = PerfilUsuario.MESTRE):
        self.id = user_id
        self.perfil = perfil
        self.email = "mestre@test"
        self.nome = "Mestre Teste"


@pytest.fixture(scope="function")
def div_custom_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    app = FastAPI()
    app.include_router(divindades_router, prefix="/api/v1")
    app.include_router(magias_router, prefix="/api/v1")

    def _override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: _UsuarioDummy(77)
    app.dependency_overrides[requer_mestre_dnd35_ou_admin] = lambda: _UsuarioDummy(77)

    yield TestClient(app)

    Base.metadata.drop_all(bind=engine)


def test_listagem_inicial_vazia(div_custom_client):
    resp = div_custom_client.get("/api/v1/divindades/custom")
    assert resp.status_code == 200
    assert resp.json() == []


def test_criar_divindade_custom_valida(div_custom_client):
    payload = {
        "nome": "Saerun",
        "titulo": "Deus da Alvorada",
        "tendencia": "Neutro e Bom",
        "dominios": ["Cura", "Sol", "Protecao"],
        "descricao": "Divindade homebrew de campanha.",
    }
    resp = div_custom_client.post("/api/v1/divindades/custom", json=payload)
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["id"] >= 1
    assert body["nome"] == "Saerun"
    assert body["label"] == "Saerun, Deus da Alvorada"
    assert body["origem"] == "custom"
    assert set(body["dominios"]) == {"Cura", "Sol", "Protecao"}


def test_criar_rejeita_nome_igual_ao_oficial(div_custom_client):
    resp = div_custom_client.post(
        "/api/v1/divindades/custom",
        json={
            "nome": "Heironeous",
            "titulo": "Outro",
            "tendencia": "Leal e Bom",
            "dominios": ["Bem"],
        },
    )
    assert resp.status_code == 400
    assert "oficial" in resp.json()["detail"].lower()


def test_criar_rejeita_tendencia_invalida(div_custom_client):
    resp = div_custom_client.post(
        "/api/v1/divindades/custom",
        json={
            "nome": "Zarathos",
            "tendencia": "Trevas",
            "dominios": ["Mal"],
        },
    )
    assert resp.status_code == 400
    assert "tend" in resp.json()["detail"].lower()


def test_criar_rejeita_dominio_desconhecido(div_custom_client):
    resp = div_custom_client.post(
        "/api/v1/divindades/custom",
        json={
            "nome": "Zarathos",
            "tendencia": "Neutro",
            "dominios": ["Batatas"],
        },
    )
    assert resp.status_code == 400
    assert "dom" in resp.json()["detail"].lower()


def test_criar_rejeita_nome_duplicado(div_custom_client):
    for _ in range(1):
        resp = div_custom_client.post(
            "/api/v1/divindades/custom",
            json={
                "nome": "Lunaris",
                "tendencia": "Neutro",
                "dominios": ["Magia", "Conhecimento"],
            },
        )
        assert resp.status_code == 201

    resp_dup = div_custom_client.post(
        "/api/v1/divindades/custom",
        json={
            "nome": "lunaris",  # mesma grafia, case diferente
            "tendencia": "Neutro",
            "dominios": ["Magia"],
        },
    )
    assert resp_dup.status_code == 400


def test_deletar_divindade_custom(div_custom_client):
    created = div_custom_client.post(
        "/api/v1/divindades/custom",
        json={
            "nome": "Umbrath",
            "tendencia": "Caótico e Mau",
            "dominios": ["Mal", "Morte"],
        },
    ).json()

    assert created["id"]
    resp_del = div_custom_client.delete(f"/api/v1/divindades/custom/{created['id']}")
    assert resp_del.status_code == 204

    resp_list = div_custom_client.get("/api/v1/divindades/custom").json()
    assert all(item["nome"] != "Umbrath" for item in resp_list)


def test_catalogo_unificado_inclui_oficial_e_custom(div_custom_client):
    div_custom_client.post(
        "/api/v1/divindades/custom",
        json={
            "nome": "Aurenhild",
            "titulo": "Deusa do Vento",
            "tendencia": "Caótico e Bom",
            "dominios": ["Ar", "Bem", "Sorte"],
        },
    )

    resp = div_custom_client.get("/api/v1/magias/divindades/catalogo")
    assert resp.status_code == 200
    catalogo = resp.json()
    nomes = {item["nome"] for item in catalogo}
    assert "Heironeous" in nomes  # oficial
    assert "Aurenhild" in nomes  # custom
    origens = {item["nome"]: item["origem"] for item in catalogo}
    assert origens["Heironeous"] == "oficial"
    assert origens["Aurenhild"] == "custom"
