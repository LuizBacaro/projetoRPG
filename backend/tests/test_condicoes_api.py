import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.games.dnd35.api.v1.condicoes import router as condicoes_router
from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.combatente_condicao import CombatenteCondicao
from app.games.dnd35.models.condicao import Condicao
from app.shared.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual
from app.shared.models.usuario import PerfilUsuario


class _UsuarioDummy:
    def __init__(self, user_id: int, perfil: PerfilUsuario | None = None):
        self.id = user_id
        self.perfil = perfil


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


def _build_client(test_db_factory, usuario: _UsuarioDummy | None = None):
    app = FastAPI()
    app.include_router(condicoes_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: usuario or _UsuarioDummy(77)

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


def test_aplicar_condicao_em_massa_mestre_em_combatente_de_terceiro(condicoes_db):
    """Mestre deve aplicar condição em combatente de outro dono (regra de mesa)."""
    db, db_factory = condicoes_db

    combatente = Combatente(
        nome="Pj do jogador",
        tipo="jogador",
        classe="Guerreiro",
        hp_atual=20,
        hp_maximo=20,
        iniciativa=3,
        dono_id=999,  # outro dono, não o mestre
    )
    condicao = Condicao(nome="Atordoado", efeito="Nao pode agir")
    db.add_all([combatente, condicao])
    db.commit()
    db.refresh(combatente)
    db.refresh(condicao)

    mestre = _UsuarioDummy(user_id=42, perfil=PerfilUsuario.MESTRE)
    client = _build_client(db_factory, usuario=mestre)
    response = client.post(
        "/api/v1/condicoes/combatentes/aplicar",
        json={
            "combatente_ids": [combatente.id],
            "condicao_id": condicao.id,
            "duracao_turnos": 2,
        },
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["total_aplicados"] == 1
    assert body["combatente_ids"] == [combatente.id]


def test_aplicar_condicao_em_massa_jogador_em_combatente_de_terceiro_bloqueado(
    condicoes_db,
):
    """Jogador comum NÃO pode aplicar condição em combatente que não é dele."""
    db, db_factory = condicoes_db

    combatente = Combatente(
        nome="Pj do mestre",
        tipo="jogador",
        classe="Mago",
        hp_atual=14,
        hp_maximo=14,
        iniciativa=4,
        dono_id=1,
    )
    condicao = Condicao(nome="Cego", efeito="-2 CA")
    db.add_all([combatente, condicao])
    db.commit()
    db.refresh(combatente)
    db.refresh(condicao)

    jogador = _UsuarioDummy(user_id=2, perfil=PerfilUsuario.JOGADOR)
    client = _build_client(db_factory, usuario=jogador)
    response = client.post(
        "/api/v1/condicoes/combatentes/aplicar",
        json={
            "combatente_ids": [combatente.id],
            "condicao_id": condicao.id,
            "duracao_turnos": 1,
        },
    )

    assert response.status_code == 403
