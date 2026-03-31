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
    assert body["magia_e_magia_dominio"] is False
    assert body["magia_dominios"] is None

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


def test_grimorio_auto_adiciona_magias_por_nivel_para_clerigo(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3  # max conjuravel clerigo: nivel 2
    db.commit()

    magia_l1 = _criar_magia(db, classe="CLERIGO", nivel=1)
    magia_l2 = Magia(nome="Magia Clerigo 2", nivel=2, classe="CLERIGO", ativo=True, descricao="desc")
    magia_l3 = Magia(nome="Magia Clerigo 3", nivel=3, classe="CLERIGO", ativo=True, descricao="desc")
    db.add_all([magia_l2, magia_l3])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magia_l2.id, classe="CLERIGO", nivel=2),
        MagiaClasse(magia_id=magia_l3.id, classe="CLERIGO", nivel=3),
    ])
    db.commit()

    client = _build_client(db_factory)

    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})
    assert listar.status_code == 200
    itens = listar.json()
    ids = {item["magia_id"] for item in itens}

    assert magia_l1.id in ids
    assert magia_l2.id in ids
    assert magia_l3.id not in ids
    assert all(item["origem"] == "AUTO_NIVEL" for item in itens)


def test_grimorio_auto_adicao_nao_duplica_em_listagens_repetidas(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Druida")
    combatente.nivel = 5  # max conjuravel druida: nivel 3
    db.commit()

    magia = _criar_magia(db, classe="DRUIDA", nivel=2)
    client = _build_client(db_factory)

    primeira = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "DRUIDA"})
    assert primeira.status_code == 200
    assert len(primeira.json()) == 1
    assert primeira.json()[0]["magia_id"] == magia.id

    segunda = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "DRUIDA"})
    assert segunda.status_code == 200
    assert len(segunda.json()) == 1
    assert segunda.json()[0]["magia_id"] == magia.id


def test_grimorio_bloqueia_ranger_abaixo_nivel_4(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Ranger")
    combatente.nivel = 3
    db.commit()
    magia = _criar_magia(db, classe="RANGER", nivel=1)
    client = _build_client(db_factory)

    criar = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia.id, "classe": "RANGER", "origem": "SELECAO_MANUAL"},
    )

    assert criar.status_code == 400
    assert "a partir do nivel 4" in criar.json()["detail"].lower()


def test_grimorio_notifica_ranger_sem_acesso_antes_nivel_4(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Ranger")
    combatente.nivel = 2
    db.commit()
    client = _build_client(db_factory)

    listar = client.get(
        f"/api/v1/grimorio/{combatente.id}/notificacoes",
        params={"classe": "RANGER"},
    )

    assert listar.status_code == 200
    itens = listar.json()
    assert any(item["tipo"] == "SEM_MAGIAS_ATE_NIVEL_4" for item in itens)


def test_grimorio_notifica_magias_adicionadas_automaticamente(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    db.commit()

    _criar_magia(db, classe="CLERIGO", nivel=1)
    client = _build_client(db_factory)

    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})
    assert listar.status_code == 200

    notificacoes = client.get(
        f"/api/v1/grimorio/{combatente.id}/notificacoes",
        params={"classe": "CLERIGO"},
    )
    assert notificacoes.status_code == 200
    itens = notificacoes.json()
    notif = next((item for item in itens if item["tipo"] == "MAGIAS_ADICIONADAS"), None)
    assert notif is not None
    assert int((notif.get("dados") or {}).get("quantidade", 0)) >= 1


def test_grimorio_limita_magias_conhecidas_feiticeiro_por_nivel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Feiticeiro")
    combatente.nivel = 1  # limite de conhecidas nivel 1 = 2
    db.commit()

    magias = [
        _criar_magia(db, classe="FEITICEIRO", nivel=1),
        Magia(nome="Magia FEITICEIRO Extra 1", nivel=1, classe="FEITICEIRO", ativo=True, descricao="desc"),
        Magia(nome="Magia FEITICEIRO Extra 2", nivel=1, classe="FEITICEIRO", ativo=True, descricao="desc"),
    ]
    db.add_all(magias[1:])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magias[1].id, classe="FEITICEIRO", nivel=1),
        MagiaClasse(magia_id=magias[2].id, classe="FEITICEIRO", nivel=1),
    ])
    db.commit()

    client = _build_client(db_factory)

    for magia in magias[:2]:
        resp = client.post(
            f"/api/v1/grimorio/{combatente.id}",
            json={"magia_id": magia.id, "classe": "FEITICEIRO", "origem": "SELECAO_MANUAL"},
        )
        assert resp.status_code == 201

    terceiro = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magias[2].id, "classe": "FEITICEIRO", "origem": "SELECAO_MANUAL"},
    )

    assert terceiro.status_code == 409
    assert "Limite de magias conhecidas" in terceiro.json()["detail"]


def test_grimorio_bloqueia_magia_acima_do_nivel_conjuravel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Feiticeiro")
    combatente.nivel = 4  # max conjuravel = 2
    db.commit()

    magia_n3 = Magia(nome="Magia FEITICEIRO N3", nivel=3, classe="FEITICEIRO", ativo=True, descricao="desc")
    db.add(magia_n3)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_n3.id, classe="FEITICEIRO", nivel=3))
    db.commit()

    client = _build_client(db_factory)
    resp = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_n3.id, "classe": "FEITICEIRO", "origem": "SELECAO_MANUAL"},
    )

    assert resp.status_code == 400
    assert "nível máximo" in resp.json()["detail"].lower() or "nivel máximo" in resp.json()["detail"].lower()


def test_grimorio_mago_nao_aplica_limite_de_conhecidas_por_nivel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Mago")
    combatente.nivel = 1
    db.commit()

    magias = [
        _criar_magia(db, classe="MAGO", nivel=1),
        Magia(nome="Magia MAGO Extra 1", nivel=1, classe="MAGO", ativo=True, descricao="desc"),
        Magia(nome="Magia MAGO Extra 2", nivel=1, classe="MAGO", ativo=True, descricao="desc"),
    ]
    db.add_all(magias[1:])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magias[1].id, classe="MAGO", nivel=1),
        MagiaClasse(magia_id=magias[2].id, classe="MAGO", nivel=1),
    ])
    db.commit()

    client = _build_client(db_factory)

    for magia in magias:
        resp = client.post(
            f"/api/v1/grimorio/{combatente.id}",
            json={"magia_id": magia.id, "classe": "MAGO", "origem": "SELECAO_MANUAL"},
        )
        assert resp.status_code == 201


def test_grimorio_filtra_auto_adicao_por_alinhamento_quando_disponivel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.alinhamento = "Leal e Bom"
    db.commit()

    magia_bloqueada = Magia(
        nome="Magia Clerigo Mal",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        descritor="Mal",
    )
    magia_permitida = Magia(
        nome="Magia Clerigo Neutra",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
    )
    db.add_all([magia_bloqueada, magia_permitida])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magia_bloqueada.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_permitida.id, classe="CLERIGO", nivel=1),
    ])
    db.commit()

    client = _build_client(db_factory)
    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})

    assert listar.status_code == 200
    ids = {item["magia_id"] for item in listar.json()}
    assert magia_permitida.id in ids
    assert magia_bloqueada.id not in ids


def test_grimorio_filtra_dominio_oposto_clerigo_quando_disponivel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.dominios = "Bem, Protecao"
    db.commit()

    magia_bem = Magia(
        nome="Magia Dominio Bem",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=True,
        dominios="Bem",
    )
    magia_mal = Magia(
        nome="Magia Dominio Mal",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=True,
        dominios="Mal",
    )
    db.add_all([magia_bem, magia_mal])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magia_bem.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_mal.id, classe="CLERIGO", nivel=1),
    ])
    db.commit()

    client = _build_client(db_factory)
    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})

    assert listar.status_code == 200
    ids = {item["magia_id"] for item in listar.json()}
    assert magia_bem.id in ids
    assert magia_mal.id not in ids


def test_grimorio_bloqueia_adicao_manual_por_alinhamento_quando_disponivel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.alinhamento = "Leal e Bom"
    db.commit()

    magia_bloqueada = Magia(
        nome="Magia Manual Mal",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        descritor="Mal",
    )
    db.add(magia_bloqueada)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_bloqueada.id, classe="CLERIGO", nivel=1))
    db.commit()

    client = _build_client(db_factory)
    resp = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_bloqueada.id, "classe": "CLERIGO", "origem": "SELECAO_MANUAL"},
    )

    assert resp.status_code == 400
    assert "alinhamento" in resp.json()["detail"].lower()
