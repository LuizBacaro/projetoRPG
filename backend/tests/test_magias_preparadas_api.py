from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.games.dnd35.api.v1.magias_preparadas import router as magias_preparadas_router
from app.shared.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.games.dnd35.models.ataque import MagiaSlot
from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.magia import Magia


@pytest.fixture(scope="function")
def prepared_db():
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
    app.include_router(magias_preparadas_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: object()
    app.dependency_overrides[requer_dono_ou_admin_combatente] = lambda: object()

    return TestClient(app)


def _criar_combatente(db, *, classe: str) -> Combatente:
    combatente = Combatente(
        nome="Teste",
        tipo="jogador",
        classe=classe,
        hp_maximo=20,
        hp_atual=20,
        iniciativa=2,
    )
    db.add(combatente)
    db.commit()
    db.refresh(combatente)
    return combatente


def _criar_magia(db, *, classe: str, nivel: int = 1) -> Magia:
    magia = Magia(nome=f"Magia {classe}", nivel=nivel, classe=classe, ativo=True)
    db.add(magia)
    db.commit()
    db.refresh(magia)
    return magia


def test_preparar_magia_bloqueia_classe_incompativel(prepared_db):
    db, db_factory = prepared_db
    combatente = _criar_combatente(db, classe="Mago")
    magia = _criar_magia(db, classe="CLÉRIGO")
    client = _build_client(db_factory)

    response = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}",
        json={"magia_id": magia.id, "nivel_slot": 1},
    )

    assert response.status_code == 400
    assert "Classe incompatível" in response.json()["detail"]


def test_preparar_magia_permite_classe_compatível(prepared_db):
    db, db_factory = prepared_db
    combatente = _criar_combatente(db, classe="Clérigo")
    magia = _criar_magia(db, classe="CLÉRIGO")
    client = _build_client(db_factory)

    response = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}",
        json={"magia_id": magia.id, "nivel_slot": 1},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["combatente_id"] == combatente.id
    assert payload["magia_id"] == magia.id


def test_preparar_magia_permite_feiticeiro_com_magia_de_mago(prepared_db):
    db, db_factory = prepared_db
    combatente = _criar_combatente(db, classe="Feiticeiro")
    magia = _criar_magia(db, classe="MAGO")
    client = _build_client(db_factory)

    response = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}",
        json={"magia_id": magia.id, "nivel_slot": 1},
    )

    assert response.status_code == 200


def test_preparar_magia_permite_combatente_multiclasse_quando_classe_bate(prepared_db):
    db, db_factory = prepared_db
    combatente = _criar_combatente(db, classe="Clérigo / Mago")
    magia = _criar_magia(db, classe="CLÉRIGO")
    client = _build_client(db_factory)

    response = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}",
        json={"magia_id": magia.id, "nivel_slot": 1, "classe": "Clérigo"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["combatente_id"] == combatente.id
    assert payload["magia_id"] == magia.id


def test_preparar_magia_aceita_quantidade_maior_que_um(prepared_db):
    db, db_factory = prepared_db
    combatente = _criar_combatente(db, classe="Mago")
    magia = _criar_magia(db, classe="MAGO")
    client = _build_client(db_factory)

    response = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}",
        json={"magia_id": magia.id, "nivel_slot": 1, "quantidade": 2},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["quantidade"] == 2
    assert payload["usos_realizados"] == 0


def test_preparar_magia_mesma_magia_atualiza_quantidade(prepared_db):
    db, db_factory = prepared_db
    combatente = _criar_combatente(db, classe="Mago")
    magia = _criar_magia(db, classe="MAGO")
    client = _build_client(db_factory)

    primeira = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}",
        json={"magia_id": magia.id, "nivel_slot": 1, "quantidade": 1},
    )
    assert primeira.status_code == 200

    segunda = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}",
        json={"magia_id": magia.id, "nivel_slot": 1, "quantidade": 3},
    )

    assert segunda.status_code == 200
    payload = segunda.json()
    assert payload["quantidade"] == 3


def test_toggle_uso_consume_e_restaura_uma_copia_por_vez(prepared_db):
    db, db_factory = prepared_db
    combatente = _criar_combatente(db, classe="Mago")
    magia = _criar_magia(db, classe="MAGO")
    client = _build_client(db_factory)

    preparar = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}",
        json={"magia_id": magia.id, "nivel_slot": 1, "quantidade": 2},
    )
    assert preparar.status_code == 200

    usar = client.patch(f"/api/v1/magias-preparadas/{combatente.id}/{magia.id}/usar?action=usar")
    assert usar.status_code == 200
    payload_usar = usar.json()
    assert payload_usar["quantidade"] == 2
    assert payload_usar["usos_realizados"] == 1
    assert payload_usar["usada"] is True

    restaurar = client.patch(f"/api/v1/magias-preparadas/{combatente.id}/{magia.id}/usar?action=restaurar")
    assert restaurar.status_code == 200
    payload_restaurar = restaurar.json()
    assert payload_restaurar["usos_realizados"] == 0
    assert payload_restaurar["usada"] is False


def test_descanso_longo_limpa_preparadas_e_reseta_slots(prepared_db):
    db, db_factory = prepared_db
    combatente = _criar_combatente(db, classe="Mago")
    magia = _criar_magia(db, classe="MAGO")
    slot = MagiaSlot(combatente_id=combatente.id, nivel=1, total=3, usados=2)
    db.add(slot)
    db.commit()
    client = _build_client(db_factory)

    preparar = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}",
        json={"magia_id": magia.id, "nivel_slot": 1, "quantidade": 2},
    )
    assert preparar.status_code == 200

    descanso = client.post(
        f"/api/v1/magias-preparadas/{combatente.id}/descanso",
        json={"confirmar": True},
    )

    assert descanso.status_code == 200
    payload = descanso.json()
    assert payload["preparadas_removidas"] == 1
    assert payload["slots_resetados"] is True

    listar = client.get(f"/api/v1/magias-preparadas/{combatente.id}")
    assert listar.status_code == 200
    assert listar.json() == []

    db.refresh(slot)
    assert slot.usados == 0
