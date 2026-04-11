from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.condicoes import router as condicoes_router
from app.core.database import Base, get_db
from app.core.deps import get_usuario_atual
from app.models.combatente import Combatente
from app.models.condicao import Condicao
from app.models.combatente_condicao import CombatenteCondicao


class _UsuarioDummy:
    def __init__(self, user_id: int):
        self.id = user_id


@pytest.fixture(scope="function")
def condicoes_db():
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
    app.include_router(condicoes_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: _UsuarioDummy(77)

    return TestClient(app)


def test_aplicar_condicao_em_massa_sucesso(condicoes_db):
    db, db_factory = condicoes_db

    c1 = Combatente(
        nome="Aldren",
        tipo="jogador",
        classe="Clerigo",
        hp_atual=18,
        hp_maximo=18,
        iniciativa=1,
        dono_id=77,
    )
    c2 = Combatente(
        nome="Borin",
        tipo="jogador",
        classe="Guerreiro",
        hp_atual=22,
        hp_maximo=22,
        iniciativa=2,
        dono_id=77,
    )
    condicao = Condicao(nome="Atordoado", efeito="Nao pode agir")

    db.add_all([c1, c2, condicao])
    db.commit()
    db.refresh(c1)
    db.refresh(c2)
    db.refresh(condicao)

    client = _build_client(db_factory)
    response = client.post(
        "/api/v1/condicoes/combatentes/aplicar",
        json={
            "combatente_ids": [c1.id, c2.id],
            "condicao_id": condicao.id,
            "duracao_turnos": 3,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body == {
        "combatente_ids": [c1.id, c2.id],
        "total_aplicados": 2,
        "condicao_id": condicao.id,
        "duracao_turnos": 3,
    }

    relacoes = (
        db.query(CombatenteCondicao)
        .filter(CombatenteCondicao.condicao_id == condicao.id)
        .all()
    )
    assert len(relacoes) == 2
    assert {r.combatente_id for r in relacoes} == {c1.id, c2.id}
    assert all(r.duracao_turnos == 3 for r in relacoes)
