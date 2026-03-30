from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker

from app.api.v1.grimorio import router as grimorio_router
from app.core.database import Base, get_db
from app.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.models.combatente import Combatente
from app.models.magia import Magia, MagiaClasse


@pytest.fixture(scope="function")
def grimorio_db():
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
    app.include_router(grimorio_router, prefix="/api/v1")

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
    magia = Magia(nome=f"Magia {classe}", nivel=nivel, classe=classe, ativo=True, descricao="desc")
    db.add(magia)
    db.flush()
    db.add(MagiaClasse(magia_id=magia.id, classe=classe, nivel=nivel))
    db.commit()
    db.refresh(magia)
    return magia


def test_grimorio_crud_basico(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Mago")
    magia = _criar_magia(db, classe="MAGO")
    client = _build_client(db_factory)

    criar = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia.id, "classe": "MAGO", "origem": "SELECAO_MANUAL"},
    )
    assert criar.status_code == 201
    body = criar.json()
    assert body["magia_id"] == magia.id

    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "MAGO"})
    assert listar.status_code == 200
    assert len(listar.json()) == 1

    atualizar = client.patch(
        f"/api/v1/grimorio/{combatente.id}/{magia.id}",
        params={"classe": "MAGO"},
        json={"favorita": True, "anotacoes": "Usar no chefe"},
    )
    assert atualizar.status_code == 200
    assert atualizar.json()["favorita"] is True

    remover = client.delete(
        f"/api/v1/grimorio/{combatente.id}/{magia.id}",
        params={"classe": "MAGO"},
    )
    assert remover.status_code == 204


def test_grimorio_bloqueia_classe_incompativel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Mago")
    magia = _criar_magia(db, classe="CLERIGO")
    client = _build_client(db_factory)

    criar = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia.id, "classe": "MAGO", "origem": "SELECAO_MANUAL"},
    )
    assert criar.status_code == 400
    assert "incompatível" in criar.json()["detail"]


def test_grimorio_troca_magia_feiticeiro_valida(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Feiticeiro")
    combatente.nivel = 4
    db.commit()

    magia_removida = _criar_magia(db, classe="FEITICEIRO", nivel=1)
    magia_nova = Magia(nome="Magia Nova FEITICEIRO", nivel=1, classe="FEITICEIRO", ativo=True, descricao="desc")
    db.add(magia_nova)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_nova.id, classe="FEITICEIRO", nivel=1))
    db.commit()
    db.refresh(magia_nova)

    client = _build_client(db_factory)
    criar = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_removida.id, "classe": "FEITICEIRO", "origem": "SELECAO_MANUAL"},
    )
    assert criar.status_code == 201

    troca = client.post(
        f"/api/v1/grimorio/{combatente.id}/troca",
        json={
            "classe": "FEITICEIRO",
            "magia_removida_id": magia_removida.id,
            "magia_adicionada_id": magia_nova.id,
        },
    )
    assert troca.status_code == 200
    body = troca.json()
    assert body["magia_removida_id"] == magia_removida.id
    assert body["magia_adicionada_id"] == magia_nova.id

    historico = client.get(
        f"/api/v1/grimorio/{combatente.id}/historico",
        params={"classe": "FEITICEIRO"},
    )
    assert historico.status_code == 200
    hist = historico.json()
    assert len(hist) == 1
    assert hist[0]["magia_removida_id"] == magia_removida.id
    assert hist[0]["magia_adicionada_id"] == magia_nova.id


def test_grimorio_troca_magia_bloqueia_nivel_invalido(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Feiticeiro")
    combatente.nivel = 4
    db.commit()

    magia_removida = _criar_magia(db, classe="FEITICEIRO", nivel=1)
    magia_nova = Magia(nome="Magia Nova Alta FEITICEIRO", nivel=2, classe="FEITICEIRO", ativo=True, descricao="desc")
    db.add(magia_nova)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_nova.id, classe="FEITICEIRO", nivel=2))
    db.commit()
    db.refresh(magia_nova)

    client = _build_client(db_factory)
    criar = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_removida.id, "classe": "FEITICEIRO", "origem": "SELECAO_MANUAL"},
    )
    assert criar.status_code == 201

    troca = client.post(
        f"/api/v1/grimorio/{combatente.id}/troca",
        json={
            "classe": "FEITICEIRO",
            "magia_removida_id": magia_removida.id,
            "magia_adicionada_id": magia_nova.id,
        },
    )
    assert troca.status_code == 400
    assert "nível" in troca.json()["detail"].lower() or "nivel" in troca.json()["detail"].lower()


def test_grimorio_notificacoes_fluxo_basico(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Feiticeiro")
    combatente.nivel = 4
    db.commit()

    client = _build_client(db_factory)

    listar = client.get(
        f"/api/v1/grimorio/{combatente.id}/notificacoes",
        params={"classe": "FEITICEIRO"},
    )
    assert listar.status_code == 200
    itens = listar.json()
    assert any(item["tipo"] == "TROCA_DISPONIVEL" for item in itens)

    notif = next(item for item in itens if item["tipo"] == "TROCA_DISPONIVEL")
    notif_id = notif["id"]

    marcar = client.patch(
        f"/api/v1/grimorio/{combatente.id}/notificacoes/{notif_id}",
        json={"lida": True},
    )
    assert marcar.status_code == 200
    assert marcar.json()["lida"] is True

    descartar = client.delete(f"/api/v1/grimorio/{combatente.id}/notificacoes/{notif_id}")
    assert descartar.status_code == 204
