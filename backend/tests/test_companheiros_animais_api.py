"""Testes da API /api/v1/companheiros-animais (D&D 3.5)."""

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.games.dnd35.api.v1.companheiros_animais import router as companheiros_router
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
    app.include_router(companheiros_router, prefix="/api/v1")

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = _usuario_admin
    app.dependency_overrides[requer_dono_ou_admin_combatente] = lambda: object()
    return TestClient(app)


def _druida(db, nivel=7):
    c = Combatente(
        nome="Druida Teste",
        tipo="jogador",
        classe="Druida",
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


def test_listar_especies(api_db_session):
    client = _build_client(api_db_session)
    r = client.get("/api/v1/companheiros-animais/especies")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 1
    assert any(e["slug"] == "lobo" for e in data)


def test_elegibilidade_druida(api_db_session):
    c = _druida(api_db_session, nivel=3)
    client = _build_client(api_db_session)
    r = client.get(f"/api/v1/companheiros-animais/{c.id}/elegibilidade")
    assert r.status_code == 200
    body = r.json()
    assert body["elegivel"] is True
    assert body["nivel_efetivo"] == 3


def test_elegibilidade_multiclasse_druida(api_db_session):
    c = Combatente(
        nome="Druida MC",
        tipo="jogador",
        classe="Druida / Guerreiro",
        raca="Humano",
        nivel=7,
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
    client = _build_client(api_db_session)
    r = client.get(f"/api/v1/companheiros-animais/{c.id}/elegibilidade")
    assert r.status_code == 200
    assert r.json()["elegivel"] is True
    criado = client.post(
        f"/api/v1/companheiros-animais/{c.id}/criar-rapido",
        json={"especie_slug": "cao", "bonus_atributos": {}, "nome": "Rex"},
    )
    assert criado.status_code == 201, criado.text


def test_elegibilidade_ranger_baixo_nivel(api_db_session):
    c = Combatente(
        nome="Ranger",
        tipo="jogador",
        classe="Ranger",
        raca="Humano",
        nivel=3,
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
    client = _build_client(api_db_session)
    r = client.get(f"/api/v1/companheiros-animais/{c.id}/elegibilidade")
    assert r.status_code == 200
    assert r.json()["elegivel"] is False


def test_calcular_e_criar_rapido(api_db_session):
    c = _druida(api_db_session, nivel=7)
    client = _build_client(api_db_session)
    calc = client.post(
        f"/api/v1/companheiros-animais/{c.id}/calcular",
        json={
            "especie_slug": "lobo",
            "bonus_atributos": {"forca": 2, "constituicao": 2},
            "nome": "Greywind",
        },
    )
    assert calc.status_code == 200, calc.text
    deriv = calc.json()["derivadas"]
    assert deriv["hd_total"] == 4
    assert deriv["bab"] == 4

    criado = client.post(
        f"/api/v1/companheiros-animais/{c.id}/criar-rapido",
        json={
            "especie_slug": "lobo",
            "bonus_atributos": {"forca": 2, "constituicao": 2},
            "nome": "Greywind",
        },
    )
    assert criado.status_code == 201, criado.text
    assert criado.json()["nome"] == "Greywind"

    obter = client.get(f"/api/v1/companheiros-animais/{c.id}")
    assert obter.status_code == 200
    assert obter.json()["especie_slug"] == "lobo"


def test_remover_companheiro(api_db_session):
    c = _druida(api_db_session)
    client = _build_client(api_db_session)
    client.post(
        f"/api/v1/companheiros-animais/{c.id}/criar-rapido",
        json={"especie_slug": "cao", "bonus_atributos": {}, "nome": "Rex"},
    )
    r = client.delete(f"/api/v1/companheiros-animais/{c.id}")
    assert r.status_code == 204
    sem = client.get(f"/api/v1/companheiros-animais/{c.id}")
    assert sem.status_code == 200
    assert sem.json() is None
