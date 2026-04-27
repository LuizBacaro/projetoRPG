from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.games.dnd35.api.v1.magias import router as magias_router
from app.shared.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual, requer_mestre_ou_admin


@pytest.fixture(scope="function")
def magias_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = TestingSessionLocal()
    try:
        yield db, TestingSessionLocal
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _build_client(test_db_factory):
    app = FastAPI()
    app.include_router(magias_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: object()
    app.dependency_overrides[requer_mestre_ou_admin] = lambda: object()

    return TestClient(app)


def _payload(nome: str, classes_niveis: list[dict]):
    return {
        "nome": nome,
        "escola": "Evocacao",
        "componentes": "V,S",
        "alcance": "medio",
        "duracao": "instantanea",
        "tempo_conjuracao": "1 acao",
        "descricao": "Descricao de teste",
        "classes_niveis": classes_niveis,
    }


def test_magias_criar_persiste_classes_e_campos_legados(magias_db):
    _, db_factory = magias_db
    client = _build_client(db_factory)

    resp = client.post(
        "/api/v1/magias",
        json=_payload(
            "Raio Arcano",
            [
                {"classe": "FEITICEIRO", "nivel": 2},
                {"classe": "MAGO", "nivel": 1},
            ],
        ),
    )

    assert resp.status_code == 201
    body = resp.json()
    assert body["nome"] == "Raio Arcano"
    assert body["classe"] == "MAGO,FEITICEIRO"
    assert body["nivel"] == 1
    assert sorted((item["classe"], item["nivel"]) for item in body["classes_niveis"]) == [
        ("FEITICEIRO", 2),
        ("MAGO", 1),
    ]


def test_magias_criar_bloqueia_nome_duplicado_case_insensitive(magias_db):
    _, db_factory = magias_db
    client = _build_client(db_factory)

    criar_1 = client.post(
        "/api/v1/magias",
        json=_payload("Misseis Magicos", [{"classe": "MAGO", "nivel": 1}]),
    )
    assert criar_1.status_code == 201

    criar_2 = client.post(
        "/api/v1/magias",
        json=_payload("misseis magicos", [{"classe": "MAGO", "nivel": 1}]),
    )
    assert criar_2.status_code == 409
    assert "Já existe" in criar_2.json()["detail"]


def test_magias_atualizar_classes_niveis_recalcula_legado(magias_db):
    _, db_factory = magias_db
    client = _build_client(db_factory)

    criar = client.post(
        "/api/v1/magias",
        json=_payload("Toque Gelido", [{"classe": "MAGO", "nivel": 1}]),
    )
    assert criar.status_code == 201
    magia_id = criar.json()["id"]

    atualizar = client.put(
        f"/api/v1/magias/{magia_id}",
        json={
            "classes_niveis": [
                {"classe": "BARDO", "nivel": 2},
                {"classe": "MAGO", "nivel": 3},
            ]
        },
    )

    assert atualizar.status_code == 200
    body = atualizar.json()
    assert body["classe"] == "BARDO,MAGO"
    assert body["nivel"] == 2
    assert sorted((item["classe"], item["nivel"]) for item in body["classes_niveis"]) == [
        ("BARDO", 2),
        ("MAGO", 3),
    ]


def test_magias_listar_ordenacao_por_nome_desc(magias_db):
    _, db_factory = magias_db
    client = _build_client(db_factory)

    for nome in ["Alpha", "Charlie", "Bravo"]:
        resp = client.post(
            "/api/v1/magias",
            json=_payload(nome, [{"classe": "MAGO", "nivel": 1}]),
        )
        assert resp.status_code == 201

    lista = client.get("/api/v1/magias", params={"sort_by": "nome", "sort_dir": "desc", "limit": 20})
    assert lista.status_code == 200

    nomes = [item["nome"] for item in lista.json()]
    assert nomes[:3] == ["Charlie", "Bravo", "Alpha"]


def test_magias_criar_rejeita_dominio_fora_lista_fixa(magias_db):
    _, db_factory = magias_db
    client = _build_client(db_factory)

    payload = _payload("Tempestade Astral", [{"classe": "CLERIGO", "nivel": 4}])
    payload["e_magia_dominio"] = True
    payload["dominios"] = "Tempo"

    resp = client.post("/api/v1/magias", json=payload)

    assert resp.status_code == 422
    assert "Dominio invalido" in resp.json()["detail"]


def test_magias_listar_dominios_retorna_lista_fixa(magias_db):
    _, db_factory = magias_db
    client = _build_client(db_factory)

    resp = client.get("/api/v1/magias/dominios")

    assert resp.status_code == 200
    body = resp.json()
    assert "Ar" in body
    assert "Magia" in body
    assert "Viagem" in body


def test_magias_listar_divindades_sugeridas_retorna_lista_fixa(magias_db):
    _, db_factory = magias_db
    client = _build_client(db_factory)

    resp = client.get("/api/v1/magias/divindades")

    assert resp.status_code == 200
    body = resp.json()
    assert "Wee Jas" in body
    assert "St. Cuthbert" in body
    assert "Obad-Hai" in body
