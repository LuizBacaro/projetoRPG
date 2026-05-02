"""Testes da API /api/v1/consumiveis (catálogo e vínculo ao combatente)."""

from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.games.dnd35.api.v1.consumiveis import router as consumiveis_router
from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.consumivel import Consumivel, ConsumivelJogador
from app.games.dnd35.schemas.consumivel import ConsumivelJogadorCreate
from app.games.dnd35.services.consumivel_service import ConsumivelService
from app.shared.core.database import Base, get_db
from app.shared.core.deps import (
    get_usuario_atual,
    requer_admin,
    requer_dono_ou_admin_combatente,
)
from app.shared.exceptions.custom_exceptions import CombatenteNaoEncontrado
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
    app.include_router(consumiveis_router, prefix="/api/v1")

    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = _usuario_admin
    app.dependency_overrides[requer_admin] = lambda: _usuario_admin()
    app.dependency_overrides[requer_dono_ou_admin_combatente] = lambda: object()

    return TestClient(app)


def test_criar_listar_e_obter_consumivel_catalogo(api_db_session):
    client = _build_client(api_db_session)
    payload = {
        "nome": "Poção de Cura",
        "descricao": "2d8+3",
        "categoria": "Poção",
        "tipo": "magico",
        "custo": "50 po",
        "peso": "0,5 kg",
        "ativo": True,
    }
    criado = client.post("/api/v1/consumiveis/", json=payload)
    assert criado.status_code == 201, criado.text
    body = criado.json()
    assert body["nome"] == "Poção de Cura"
    cid = body["id"]

    lista = client.get("/api/v1/consumiveis/")
    assert lista.status_code == 200
    assert len(lista.json()) == 1

    um = client.get(f"/api/v1/consumiveis/{cid}")
    assert um.status_code == 200
    assert um.json()["id"] == cid


def test_obter_consumivel_inexistente_404(api_db_session):
    client = _build_client(api_db_session)
    r = client.get("/api/v1/consumiveis/999")
    assert r.status_code == 404


def test_listar_filtro_tipo_oleo_casa_titulo_unicode_sqlite(api_db_session):
    """SQLite não faz ILIKE case-fold em Unicode; tipo 'Óleo' deve aparecer com ?tipo=óleo."""
    api_db_session.add(
        Consumivel(nome="Óleo da Escuridão", tipo="Óleo", ativo=True)
    )
    api_db_session.commit()
    client = _build_client(api_db_session)
    r = client.get("/api/v1/consumiveis/", params={"tipo": "óleo"})
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["nome"] == "Óleo da Escuridão"
    assert data[0]["tipo"] == "Óleo"


def test_deletar_catalogo_soft_delete(api_db_session):
    client = _build_client(api_db_session)
    criado = client.post(
        "/api/v1/consumiveis/",
        json={
            "nome": "Antitoxina",
            "descricao": None,
            "ativo": True,
        },
    )
    assert criado.status_code == 201
    cid = criado.json()["id"]

    rem = client.delete(f"/api/v1/consumiveis/catalogo/{cid}")
    assert rem.status_code == 204

    r = client.get(f"/api/v1/consumiveis/{cid}")
    assert r.status_code == 404


def test_fluxo_jogador_adicionar_listar_remover(api_db_session):
    combatente = Combatente(
        nome="Elara",
        tipo="jogador",
        classe="Clérigo",
        hp_maximo=40,
        hp_atual=40,
        iniciativa=10,
        dono_id=1,
    )
    api_db_session.add(combatente)
    api_db_session.commit()

    client = _build_client(api_db_session)
    cat = client.post(
        "/api/v1/consumiveis/",
        json={"nome": "Fogo Alquímico", "tipo": "item", "ativo": True},
    )
    assert cat.status_code == 201
    consumivel_id = cat.json()["id"]

    ad = client.post(
        f"/api/v1/consumiveis/{combatente.id}/adicionar",
        json={"consumivel_id": consumivel_id, "quantidade": 2},
    )
    assert ad.status_code == 201
    assert ad.json()["quantidade"] == 2
    assert ad.json()["nome"] == "Fogo Alquímico"

    lst = client.get(f"/api/v1/consumiveis/{combatente.id}/listar")
    assert lst.status_code == 200
    assert len(lst.json()) == 1
    assert lst.json()[0]["quantidade"] == 2

    rm = client.delete(
        f"/api/v1/consumiveis/{combatente.id}/remover/{consumivel_id}",
    )
    assert rm.status_code == 204

    vazio = client.get(f"/api/v1/consumiveis/{combatente.id}/listar")
    assert vazio.status_code == 200
    assert vazio.json() == []


def test_adicionar_consumivel_catalogo_inexistente_400(api_db_session):
    combatente = Combatente(
        nome="Karn",
        tipo="jogador",
        classe="Guerreiro",
        hp_maximo=50,
        hp_atual=50,
        iniciativa=5,
        dono_id=1,
    )
    api_db_session.add(combatente)
    api_db_session.commit()

    client = _build_client(api_db_session)
    r = client.post(
        f"/api/v1/consumiveis/{combatente.id}/adicionar",
        json={"consumivel_id": 99999, "quantidade": 1},
    )
    assert r.status_code == 400
    assert "não encontrado" in r.json()["detail"].lower()


class _CombatenteRepoVazio:
    def get_by_id(self, entity_id: int):
        return None


def test_servico_exige_combatente_via_repositorio(api_db_session):
    svc = ConsumivelService(api_db_session, combatente_repo=_CombatenteRepoVazio())
    with pytest.raises(CombatenteNaoEncontrado):
        svc.listar_jogador(1)
    with pytest.raises(CombatenteNaoEncontrado):
        svc.remover_jogador(1, 1)
    with pytest.raises(CombatenteNaoEncontrado):
        svc.adicionar_jogador(1, ConsumivelJogadorCreate(consumivel_id=1, quantidade=1))
