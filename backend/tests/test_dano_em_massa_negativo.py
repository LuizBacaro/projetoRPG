"""Reproduz o bug de aplicar dano em massa quando combatente está em 0 HP.

Cenário relatado: PJ em 0/35 sofre dano em massa e API retorna 500.
Esperado: backend deve aceitar e clampar HP entre -10 e 0 conforme D&D 3.5.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.games.dnd35.api.v1.combatentes import router as combatentes_router
from app.games.dnd35.models.combatente import Combatente
from app.shared.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente


class _UsuarioDummy:
    def __init__(self, user_id: int = 77):
        self.id = user_id
        self.perfil = None


@pytest.fixture
def db_factory():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    yield factory
    Base.metadata.drop_all(bind=engine)


def _build_client(db_factory):
    app = FastAPI()
    app.include_router(combatentes_router, prefix="/api/v1")

    def _override_get_db():
        db = db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: _UsuarioDummy()
    app.dependency_overrides[requer_dono_ou_admin_combatente] = lambda: object()
    return TestClient(app)


def _criar_combatente_em_zero(db_factory) -> int:
    db = db_factory()
    try:
        combatente = Combatente(
            nome="Theron Caído",
            tipo="jogador",
            classe="Guerreiro",
            hp_atual=0,
            hp_maximo=35,
            iniciativa=2,
            dono_id=77,
        )
        db.add(combatente)
        db.commit()
        db.refresh(combatente)
        return combatente.id
    finally:
        db.close()


def test_dano_em_massa_em_combatente_zerado_aceita_e_clampa(db_factory):
    """0 HP → -5 HP via dano em massa: deve passar (regra D&D 3.5).

    Regressão de #fix-hp-negativo: a constraint legada
    `ck_combatentes_hp_atual_non_negative` (CHECK hp_atual >= 0) bloqueava
    o UPDATE com IntegrityError 500 mesmo após o service clampar até -10.
    """
    combatente_id = _criar_combatente_em_zero(db_factory)
    client = _build_client(db_factory)

    response = client.post(
        "/api/v1/combatentes/dano/massa",
        json={"combatente_ids": [combatente_id], "valor": 5},
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total"] == 1
    assert body["resultados"][0]["hp_atual"] == -5
    assert body["resultados"][0]["hp_maximo"] == 35


def test_dano_em_massa_excessivo_clampa_em_menos_dez(db_factory):
    combatente_id = _criar_combatente_em_zero(db_factory)
    client = _build_client(db_factory)

    response = client.post(
        "/api/v1/combatentes/dano/massa",
        json={"combatente_ids": [combatente_id], "valor": 999},
    )

    assert response.status_code == 200, response.text
    assert response.json()["resultados"][0]["hp_atual"] == -10


def test_dano_em_massa_em_monstro_zerado_segue_em_zero(db_factory):
    db = db_factory()
    try:
        monstro = Combatente(
            nome="Goblin",
            tipo="monstro",
            classe="Goblin",
            hp_atual=0,
            hp_maximo=8,
            iniciativa=12,
            dono_id=77,
        )
        db.add(monstro)
        db.commit()
        db.refresh(monstro)
        monstro_id = monstro.id
    finally:
        db.close()

    client = _build_client(db_factory)
    response = client.post(
        "/api/v1/combatentes/dano/massa",
        json={"combatente_ids": [monstro_id], "valor": 5},
    )

    assert response.status_code == 200, response.text
    assert response.json()["resultados"][0]["hp_atual"] == 0
