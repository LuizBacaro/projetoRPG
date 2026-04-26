from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.armaduras_protecao import router as armaduras_router
from app.core.database import Base
from app.core.database import get_db
from app.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.games.dnd35.models.armadura_protecao import ArmaduraProtecao, ArmaduraProtecaoJogador  # noqa: F401
from app.games.dnd35.models.combatente import Combatente


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


def _build_client(db_session):
    app = FastAPI()
    app.include_router(armaduras_router, prefix="/api/v1")

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: SimpleNamespace(id=1, perfil="ADMINISTRADOR")
    app.dependency_overrides[requer_dono_ou_admin_combatente] = lambda: object()

    return TestClient(app)


def test_armaduras_protecao_criar_e_listar_catalogo(api_db_session):
    client = _build_client(api_db_session)
    payload = {
        "nome": "Cota de Malha",
        "tipo": "Armadura média",
        "bonus_ca": 5,
        "des_max": "+2",
        "penalidade": -4,
        "falha_arcana": "30%",
        "deslocamento": "6m",
        "peso": 20.0,
        "propriedades_especiais": "Metálica",
        "ativo": True,
    }

    criado = client.post("/api/v1/armaduras_protecao/", json=payload)
    assert criado.status_code == 201
    criado_json = criado.json()
    assert criado_json["nome"] == "Cota de Malha"
    assert criado_json["bonus_ca"] == 5

    listagem = client.get("/api/v1/armaduras_protecao/")
    assert listagem.status_code == 200
    itens = listagem.json()
    assert len(itens) == 1
    assert itens[0]["nome"] == "Cota de Malha"


def test_armaduras_protecao_fluxo_jogador_adicionar_listar_bonus_e_remover(api_db_session):
    combatente = Combatente(
        nome="Thoran",
        tipo="jogador",
        classe="Guerreiro",
        hp_maximo=30,
        hp_atual=30,
        iniciativa=2,
        dono_id=1,
    )
    api_db_session.add(combatente)
    api_db_session.commit()

    client = _build_client(api_db_session)

    item_payload = {
        "nome": "Escudo Pesado",
        "tipo": "Escudo",
        "bonus_ca": 2,
        "des_max": None,
        "penalidade": -2,
        "falha_arcana": "15%",
        "deslocamento": None,
        "peso": 7.5,
        "propriedades_especiais": "Concede cobertura parcial",
        "ativo": True,
    }
    criado = client.post("/api/v1/armaduras_protecao/", json=item_payload)
    assert criado.status_code == 201
    item_id = criado.json()["id"]

    adicionar = client.post(
        f"/api/v1/armaduras_protecao/{combatente.id}/adicionar",
        json={"item_id": item_id},
    )
    assert adicionar.status_code == 201
    assert adicionar.json()["id"] == item_id

    listar_jogador = client.get(f"/api/v1/armaduras_protecao/{combatente.id}/listar")
    assert listar_jogador.status_code == 200
    assert len(listar_jogador.json()) == 1
    assert listar_jogador.json()[0]["bonus_ca"] == 2

    bonus = client.get(f"/api/v1/armaduras_protecao/{combatente.id}/bonus-ca")
    assert bonus.status_code == 200
    assert bonus.json()["bonus_ca_total"] == 2
    api_db_session.refresh(combatente)
    assert combatente.toque == 10
    assert combatente.surpresa == 12
    assert combatente.ca == 12

    remover = client.delete(f"/api/v1/armaduras_protecao/{combatente.id}/remover/{item_id}")
    assert remover.status_code == 204

    bonus_final = client.get(f"/api/v1/armaduras_protecao/{combatente.id}/bonus-ca")
    assert bonus_final.status_code == 200
    assert bonus_final.json()["bonus_ca_total"] == 0
    api_db_session.refresh(combatente)
    assert combatente.toque == 10
    assert combatente.surpresa == 10
    assert combatente.ca == 10
