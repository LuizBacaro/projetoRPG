"""Testes da API /api/v1/familiares (D&D 3.5)."""

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.games.dnd35.api.v1.familiares import router as familiares_router
from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.companheiro_animal import CompanheiroAnimal
from app.shared.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.shared.models.usuario import PerfilUsuario


@pytest.fixture(scope="function")
def api_db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = testing_session_local()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _usuario_admin():
    return SimpleNamespace(id=1, perfil=PerfilUsuario.ADMINISTRADOR, email="admin@test")


def _build_client(db_session):
    app = FastAPI()
    app.include_router(familiares_router, prefix="/api/v1")

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = _usuario_admin
    app.dependency_overrides[requer_dono_ou_admin_combatente] = lambda: object()
    return TestClient(app)


def _mago(db, nivel=5):
    c = Combatente(
        nome="Mago Teste",
        tipo="jogador",
        classe="Mago",
        raca="Humano",
        nivel=nivel,
        forca=10,
        destreza=10,
        constituicao=10,
        inteligencia=10,
        sabedoria=10,
        carisma=10,
        hp_atual=20,
        hp_maximo=20,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_listar_especies_familiar(api_db_session):
    client = _build_client(api_db_session)
    r = client.get("/api/v1/familiares/especies")
    assert r.status_code == 200
    assert any(e["slug"] == "coruja" for e in r.json())


def test_criar_familiar_mago(api_db_session):
    c = _mago(api_db_session)
    client = _build_client(api_db_session)
    criado = client.post(
        f"/api/v1/familiares/{c.id}/criar-rapido",
        json={"especie_slug": "coruja", "nome": "Hoot"},
    )
    assert criado.status_code == 201, criado.text
    assert criado.json()["nome"] == "Hoot"
    assert criado.json()["inteligencia"] >= 6


def test_bloqueio_companheiro_existente(api_db_session):
    c = Combatente(
        nome="Híbrido",
        tipo="jogador",
        classe="Mago",
        raca="Humano",
        nivel=5,
        forca=10,
        destreza=10,
        constituicao=10,
        inteligencia=10,
        sabedoria=10,
        carisma=10,
        hp_atual=20,
        hp_maximo=20,
    )
    api_db_session.add(c)
    api_db_session.commit()
    api_db_session.refresh(c)
    api_db_session.add(
        CompanheiroAnimal(
            combatente_id=c.id,
            especie_slug="lobo",
            nome="Wolf",
            forca=10,
            destreza=10,
            constituicao=10,
            inteligencia=2,
            sabedoria=10,
            carisma=6,
            hp_atual=10,
            hp_maximo=10,
            ca=12,
        )
    )
    api_db_session.commit()
    client = _build_client(api_db_session)
    r = client.post(
        f"/api/v1/familiares/{c.id}/criar-rapido",
        json={"especie_slug": "gato", "nome": "Miau"},
    )
    assert r.status_code == 400
    assert "companheiro" in r.json()["detail"].lower()
