from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.combatentes import router as combatentes_router
from app.core.database import Base, get_db
from app.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente


class _UsuarioDummy:
    def __init__(self, user_id: int):
        self.id = user_id


@pytest.fixture(scope="function")
def combatentes_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = testing_session_local()
    try:
        yield db, testing_session_local
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _build_client(test_db_factory):
    app = FastAPI()
    app.include_router(combatentes_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: _UsuarioDummy(77)
    app.dependency_overrides[requer_dono_ou_admin_combatente] = lambda: object()

    return TestClient(app)


def _combatente_payload(**overrides):
    payload = {
        "nome": "Irmão Aldren",
        "tipo": "jogador",
        "classe": "Clérigo",
        "raca": "Humano",
        "divindade": "St. Cuthbert",
        "alinhamento": "Leal e Bom",
        "dominios": "Cura, Proteção",
        "hp_maximo": "18",
        "iniciativa": "1",
        "ca": "16",
        "toque": "11",
        "surpresa": "15",
        "forca": "10",
        "destreza": "12",
        "constituicao": "14",
        "inteligencia": "10",
        "sabedoria": "17",
        "carisma": "13",
        "fortitude": "4",
        "reflexos": "1",
        "vontade": "6",
        "nivel": "5",
        "pontos": "0",
    }
    payload.update(overrides)
    return payload


def test_criar_combatente_retorna_alinhamento_e_dominios(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    response = client.post("/api/v1/combatentes", data=_combatente_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["dono_id"] == 77
    assert body["divindade"] == "St. Cuthbert"
    assert body["alinhamento"] == "Leal e Bom"
    assert body["dominios"] == "Cura, Proteção"
    assert body["hp_atual"] == 18


def test_atualizar_combatente_persiste_alinhamento_e_dominios_editados(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    criado = client.post("/api/v1/combatentes", data=_combatente_payload())
    combatente_id = criado.json()["id"]

    atualizar = client.put(
        f"/api/v1/combatentes/{combatente_id}",
        data=_combatente_payload(
            divindade="Wee Jas",
            alinhamento="Neutro e Bom",
            dominios="Cura, Sol",
            sabedoria="18",
        ),
    )

    assert atualizar.status_code == 200
    body = atualizar.json()
    assert body["divindade"] == "Wee Jas"
    assert body["alinhamento"] == "Neutro e Bom"
    assert body["dominios"] == "Cura, Sol"
    assert body["sabedoria"] == 18

    obter = client.get(f"/api/v1/combatentes/{combatente_id}")

    assert obter.status_code == 200
    assert obter.json()["divindade"] == "Wee Jas"
    assert obter.json()["alinhamento"] == "Neutro e Bom"
    assert obter.json()["dominios"] == "Cura, Sol"