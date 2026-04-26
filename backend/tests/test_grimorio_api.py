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


def _criar_combatente(db, *, classe: str, nivel: int = 1) -> Combatente:
    combatente = Combatente(
        nome="Teste",
        tipo="jogador",
        classe=classe,
        nivel=nivel,
        hp_maximo=20,
        hp_atual=20,
        iniciativa=2,
    )
    db.add(combatente)
    db.commit()
    db.refresh(combatente)
    return combatente


def _criar_magia(
    db,
    *,
    classe: str,
    nivel: int = 1,
    nome: str | None = None,
    escola: str | None = None,
    componentes: str | None = None,
    descricao: str | None = None,
) -> Magia:
    magia = Magia(
        nome=nome or f"Magia {classe}",
        nivel=nivel,
        classe=classe,
        ativo=True,
        escola=escola,
        componentes=componentes,
        descricao=descricao or "desc",
    )
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
    assert body["descricao"] == "desc"
    assert body["resistencia_magia"] is None

    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "MAGO"})
    assert listar.status_code == 200
    assert len(listar.json()) == 1
    assert listar.headers["X-Total-Count"] == "1"
    assert listar.headers["X-Skip"] == "0"
    assert listar.headers["X-Limit"] == "1"


def test_grimorio_lista_paginada_preserva_corpo_e_headers(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Mago")
    client = _build_client(db_factory)

    magias = [
        _criar_magia(db, classe="MAGO", nome="Magia MAGO 1"),
        _criar_magia(db, classe="MAGO", nome="Magia MAGO 2"),
        _criar_magia(db, classe="MAGO", nome="Magia MAGO 3"),
    ]

    for magia in magias:
        criar = client.post(
            f"/api/v1/grimorio/{combatente.id}",
            json={"magia_id": magia.id, "classe": "MAGO", "origem": "SELECAO_MANUAL"},
        )
        assert criar.status_code == 201

    listar_completo = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "MAGO"})
    assert listar_completo.status_code == 200
    assert isinstance(listar_completo.json(), list)
    assert len(listar_completo.json()) == 3
    assert listar_completo.headers["X-Total-Count"] == "3"
    assert listar_completo.headers["X-Skip"] == "0"
    assert listar_completo.headers["X-Limit"] == "3"

    listar_paginado = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "skip": 1, "limit": 1},
    )
    assert listar_paginado.status_code == 200
    body = listar_paginado.json()
    assert isinstance(body, list)
    assert len(body) == 1
    assert body[0]["magia_nome"] == "Magia MAGO 2"
    assert listar_paginado.headers["X-Total-Count"] == "3"
    assert listar_paginado.headers["X-Skip"] == "1"
    assert listar_paginado.headers["X-Limit"] == "1"

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


def test_grimorio_lista_filtra_por_campos_e_magia_ids(grimorio_db):
    db, db_factory = grimorio_db
    # Mago nível 5 conjura até 3º nível; o teste inclui magias de nível 2 e 3.
    combatente = _criar_combatente(db, classe="Mago", nivel=5)
    client = _build_client(db_factory)

    magia_evocacao = _criar_magia(
        db,
        classe="MAGO",
        nivel=3,
        nome="Bola de Fogo",
        escola="Evocacao",
        componentes="V,S,M",
        descricao="Explosao de fogo em area",
    )
    magia_transmutacao = _criar_magia(
        db,
        classe="MAGO",
        nivel=2,
        nome="Pele Rochosa",
        escola="Transmutacao",
        componentes="V,S",
        descricao="Fortalece a pele com runas antigas",
    )
    magia_ilusao = _criar_magia(
        db,
        classe="MAGO",
        nivel=1,
        nome="Imagem Silenciosa",
        escola="Ilusao",
        componentes="V,S,F",
        descricao="Cria uma imagem ilusoria controlada",
    )

    for magia in (magia_evocacao, magia_transmutacao, magia_ilusao):
        criar = client.post(
            f"/api/v1/grimorio/{combatente.id}",
            json={"magia_id": magia.id, "classe": "MAGO", "origem": "SELECAO_MANUAL"},
        )
        assert criar.status_code == 201

    atualizar = client.patch(
        f"/api/v1/grimorio/{combatente.id}/{magia_transmutacao.id}",
        params={"classe": "MAGO"},
        json={"favorita": True, "anotacoes": "Runas para chefe final"},
    )
    assert atualizar.status_code == 200

    filtrar_nome_magia = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "nome": "bola"},
    )
    assert filtrar_nome_magia.status_code == 200
    assert [item["magia_id"] for item in filtrar_nome_magia.json()] == [magia_evocacao.id]

    filtrar_nome_escola = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "nome": "transmut"},
    )
    assert filtrar_nome_escola.status_code == 200
    assert [item["magia_id"] for item in filtrar_nome_escola.json()] == [magia_transmutacao.id]

    filtrar_nome_descricao = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "nome": "ilusoria"},
    )
    assert filtrar_nome_descricao.status_code == 200
    assert [item["magia_id"] for item in filtrar_nome_descricao.json()] == [magia_ilusao.id]

    filtrar_nome_anotacoes = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "nome": "runas"},
    )
    assert filtrar_nome_anotacoes.status_code == 200
    assert [item["magia_id"] for item in filtrar_nome_anotacoes.json()] == [magia_transmutacao.id]

    filtrar_nivel = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "nivel": 2},
    )
    assert filtrar_nivel.status_code == 200
    assert [item["magia_id"] for item in filtrar_nivel.json()] == [magia_transmutacao.id]

    filtrar_escola = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "escola": "Ilusao"},
    )
    assert filtrar_escola.status_code == 200
    assert [item["magia_id"] for item in filtrar_escola.json()] == [magia_ilusao.id]

    filtrar_componentes = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "componentes": "M"},
    )
    assert filtrar_componentes.status_code == 200
    assert [item["magia_id"] for item in filtrar_componentes.json()] == [magia_evocacao.id]

    filtrar_favorita = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "favorita": True},
    )
    assert filtrar_favorita.status_code == 200
    assert [item["magia_id"] for item in filtrar_favorita.json()] == [magia_transmutacao.id]

    filtrar_ids_csv = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params={"classe": "MAGO", "magia_ids": f"{magia_evocacao.id},{magia_ilusao.id}"},
    )
    assert filtrar_ids_csv.status_code == 200
    assert {item["magia_id"] for item in filtrar_ids_csv.json()} == {magia_evocacao.id, magia_ilusao.id}

    filtrar_ids_lista = client.get(
        f"/api/v1/grimorio/{combatente.id}",
        params=[
            ("classe", "MAGO"),
            ("magia_ids", str(magia_transmutacao.id)),
            ("magia_ids", str(magia_ilusao.id)),
            ("skip", "0"),
            ("limit", "1"),
        ],
    )
    assert filtrar_ids_lista.status_code == 200
    body = filtrar_ids_lista.json()
    assert len(body) == 1
    assert body[0]["magia_id"] == magia_transmutacao.id
    assert filtrar_ids_lista.headers["X-Total-Count"] == "2"
    assert filtrar_ids_lista.headers["X-Skip"] == "0"
    assert filtrar_ids_lista.headers["X-Limit"] == "1"


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


def test_grimorio_lista_clerigo_com_parametro_acentuado(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clérigo")
    combatente.nivel = 3
    db.commit()

    magia_l1 = _criar_magia(db, classe="CLERIGO", nivel=1)
    client = _build_client(db_factory)

    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "Clérigo"})
    assert listar.status_code == 200
    itens = listar.json()
    ids = {item["magia_id"] for item in itens}

    assert magia_l1.id in ids


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


def test_grimorio_notificacao_magias_adicionadas_inclui_nomes(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    db.commit()

    magia = Magia(nome="Luz Sagrada", nivel=1, classe="CLERIGO", ativo=True, descricao="desc")
    db.add(magia)
    db.flush()
    db.add(MagiaClasse(magia_id=magia.id, classe="CLERIGO", nivel=1))
    db.commit()

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

    dados = notif.get("dados") or {}
    nomes = dados.get("magias_nomes") or []
    assert isinstance(nomes, list)
    assert "Luz Sagrada" in nomes


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


def test_grimorio_mago_bloqueia_adicao_acima_nivel_conjuravel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Mago")
    combatente.nivel = 1  # max conjuravel = 1
    db.commit()

    magia_n2 = Magia(nome="Mago N2", nivel=2, classe="MAGO", ativo=True, descricao="desc")
    db.add(magia_n2)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_n2.id, classe="MAGO", nivel=2))
    db.commit()

    client = _build_client(db_factory)
    resp = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_n2.id, "classe": "MAGO", "origem": "SELECAO_MANUAL"},
    )

    assert resp.status_code == 400
    assert "nível máximo" in resp.json()["detail"].lower() or "nivel máximo" in resp.json()["detail"].lower()


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
        dominios="Mal",
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
        dominios="Mal",
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


def test_grimorio_remove_automatico_por_alinhamento_apos_mudanca(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.alinhamento = "Neutro e Mau"
    db.commit()

    magia_mal = Magia(
        nome="Magia Permitida Antes da Mudanca",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Mal",
    )
    db.add(magia_mal)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_mal.id, classe="CLERIGO", nivel=1))
    db.commit()

    client = _build_client(db_factory)
    criar = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_mal.id, "classe": "CLERIGO", "origem": "SELECAO_MANUAL"},
    )
    assert criar.status_code == 201

    combatente.alinhamento = "Leal e Bom"
    db.commit()

    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})
    assert listar.status_code == 200
    assert all(item["magia_id"] != magia_mal.id for item in listar.json())


def test_grimorio_neutro_verdadeiro_bloqueia_todas_tendencias(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.alinhamento = "Neutro"
    db.commit()

    magia_bem = Magia(
        nome="Magia Bem Neutro",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Bem",
    )
    magia_mal = Magia(
        nome="Magia Mal Neutro",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Mal",
    )
    magia_ordem = Magia(
        nome="Magia Ordem Neutro",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Ordem",
    )
    magia_caos = Magia(
        nome="Magia Caos Neutro",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Caos",
    )
    magia_neutra = Magia(
        nome="Magia Neutra",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
    )
    db.add_all([magia_bem, magia_mal, magia_ordem, magia_caos, magia_neutra])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magia_bem.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_mal.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_ordem.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_caos.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_neutra.id, classe="CLERIGO", nivel=1),
    ])
    db.commit()

    client = _build_client(db_factory)
    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})

    assert listar.status_code == 200
    ids = {item["magia_id"] for item in listar.json()}
    assert magia_neutra.id in ids
    assert magia_bem.id not in ids
    assert magia_mal.id not in ids
    assert magia_ordem.id not in ids
    assert magia_caos.id not in ids


def test_grimorio_leal_neutro_bloqueia_bem_mal_e_caos(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.alinhamento = "Leal e Neutro"
    db.commit()

    magia_bem = Magia(
        nome="Magia Bem Leal Neutro",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Bem",
    )
    magia_mal = Magia(
        nome="Magia Mal Leal Neutro",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Mal",
    )
    magia_caos = Magia(
        nome="Magia Caos Leal Neutro",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Caos",
    )
    magia_ordem = Magia(
        nome="Magia Ordem Leal Neutro",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Ordem",
    )
    db.add_all([magia_bem, magia_mal, magia_caos, magia_ordem])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magia_bem.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_mal.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_caos.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_ordem.id, classe="CLERIGO", nivel=1),
    ])
    db.commit()

    client = _build_client(db_factory)
    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})

    assert listar.status_code == 200
    ids = {item["magia_id"] for item in listar.json()}
    assert magia_ordem.id in ids
    assert magia_bem.id not in ids
    assert magia_mal.id not in ids
    assert magia_caos.id not in ids


def test_grimorio_remove_automatico_por_dominio_oposto_apos_mudanca(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.dominios = "Bem, Protecao"
    db.commit()

    magia_bem = Magia(
        nome="Magia Dominio Bem Reconciliacao",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=True,
        dominios="Bem",
    )
    db.add(magia_bem)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_bem.id, classe="CLERIGO", nivel=1))
    db.commit()

    client = _build_client(db_factory)
    criar = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_bem.id, "classe": "CLERIGO", "origem": "SELECAO_MANUAL"},
    )
    assert criar.status_code == 201

    combatente.dominios = "Mal, Protecao"
    db.commit()

    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})
    assert listar.status_code == 200
    assert all(item["magia_id"] != magia_bem.id for item in listar.json())


def test_grimorio_notificacao_selecao_pendente_inclui_niveis(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Feiticeiro")
    combatente.nivel = 4
    db.commit()

    # Em produção, magias de Feiticeiro são armazenadas com classe="MAGO"
    # (Feiticeiro compartilha a lista do Mago em D&D 3.5).
    magia_n0 = Magia(nome="Magia FEITICEIRO N0", nivel=0, classe="MAGO", ativo=True, descricao="desc")
    magia_n1 = Magia(nome="Magia FEITICEIRO N1", nivel=1, classe="MAGO", ativo=True, descricao="desc")
    magia_n2 = Magia(nome="Magia FEITICEIRO N2", nivel=2, classe="MAGO", ativo=True, descricao="desc")
    db.add_all([magia_n0, magia_n1, magia_n2])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magia_n0.id, classe="MAGO", nivel=0),
        MagiaClasse(magia_id=magia_n1.id, classe="MAGO", nivel=1),
        MagiaClasse(magia_id=magia_n2.id, classe="MAGO", nivel=2),
    ])
    db.commit()

    client = _build_client(db_factory)
    listar = client.get(
        f"/api/v1/grimorio/{combatente.id}/notificacoes",
        params={"classe": "FEITICEIRO"},
    )

    assert listar.status_code == 200
    itens = listar.json()
    notif = next((item for item in itens if item["tipo"] == "SELECAO_PENDENTE"), None)
    assert notif is not None

    dados = notif.get("dados") or {}
    assert int(dados.get("quantidade_pendente", 0)) > 0
    por_nivel = dados.get("por_nivel")
    assert isinstance(por_nivel, dict)
    assert len(por_nivel) > 0


def test_grimorio_notificacao_conversao_divina_por_alinhamento_neutro(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.alinhamento = "Neutro"
    db.commit()

    client = _build_client(db_factory)
    resp = client.get(
        f"/api/v1/grimorio/{combatente.id}/notificacoes",
        params={"classe": "CLERIGO"},
    )

    assert resp.status_code == 200
    itens = resp.json()
    notif = next((item for item in itens if item["tipo"] == "CONVERSAO_DIVINA"), None)
    assert notif is not None
    assert notif["dados"].get("modo") == "ESCOLHER_CURAR_OU_INFLIGIR"
    assert notif["dados"].get("fonte") == "ALINHAMENTO"


def test_grimorio_notificacao_conversao_divina_por_excecao_wee_jas(monkeypatch, grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.alinhamento = "Leal e Neutro"
    db.commit()

    from app.games.dnd35.services import grimorio_service as grimorio_mod
    monkeypatch.setattr(grimorio_mod, "_divindade_do_combatente", lambda _c: "Wee Jas")

    client = _build_client(db_factory)
    resp = client.get(
        f"/api/v1/grimorio/{combatente.id}/notificacoes",
        params={"classe": "CLERIGO"},
    )

    assert resp.status_code == 200
    itens = resp.json()
    notif = next((item for item in itens if item["tipo"] == "CONVERSAO_DIVINA"), None)
    assert notif is not None
    assert notif["dados"].get("modo") == "INFLIGIR_OBRIGATORIO"
    assert notif["dados"].get("fonte") == "DIVINDADE"


def test_grimorio_clerigo_auto_adiciona_apenas_dominios_escolhidos_no_nivel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3  # max conjuravel: nivel 2
    combatente.dominios = "Bem, Protecao"
    db.commit()

    magia_base = Magia(
        nome="Magia Clerigo Base",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=False,
    )
    magia_bem = Magia(
        nome="Magia Dominio Bem N1",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=True,
        dominios="Bem",
    )
    magia_protecao = Magia(
        nome="Magia Dominio Protecao N2",
        nivel=2,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=True,
        dominios="Protecao",
    )
    magia_mal = Magia(
        nome="Magia Dominio Mal N1",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=True,
        dominios="Mal",
    )
    magia_guerra = Magia(
        nome="Magia Dominio Guerra N2",
        nivel=2,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=True,
        dominios="Guerra",
    )
    db.add_all([magia_base, magia_bem, magia_protecao, magia_mal, magia_guerra])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magia_base.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_bem.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_protecao.id, classe="CLERIGO", nivel=2),
        MagiaClasse(magia_id=magia_mal.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_guerra.id, classe="CLERIGO", nivel=2),
    ])
    db.commit()

    client = _build_client(db_factory)
    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})

    assert listar.status_code == 200
    itens = listar.json()
    ids = {item["magia_id"] for item in itens}

    assert magia_base.id in ids
    assert magia_bem.id in ids
    assert magia_protecao.id in ids
    assert magia_mal.id not in ids
    assert magia_guerra.id not in ids


def test_grimorio_clerigo_adiciona_magia_de_dominio_ao_subir_nivel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3  # max conjuravel: nivel 2
    combatente.dominios = "Bem, Protecao"
    db.commit()

    magia_bem_n2 = Magia(
        nome="Magia Dominio Bem N2",
        nivel=2,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=True,
        dominios="Bem",
    )
    magia_bem_n3 = Magia(
        nome="Magia Dominio Bem N3",
        nivel=3,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=True,
        dominios="Bem",
    )
    db.add_all([magia_bem_n2, magia_bem_n3])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magia_bem_n2.id, classe="CLERIGO", nivel=2),
        MagiaClasse(magia_id=magia_bem_n3.id, classe="CLERIGO", nivel=3),
    ])
    db.commit()

    client = _build_client(db_factory)

    primeira = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})
    assert primeira.status_code == 200
    ids_primeira = {item["magia_id"] for item in primeira.json()}
    assert magia_bem_n2.id in ids_primeira
    assert magia_bem_n3.id not in ids_primeira

    combatente.nivel = 5  # max conjuravel: nivel 3
    db.commit()

    segunda = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})
    assert segunda.status_code == 200
    itens_segunda = segunda.json()
    ids_segunda = {item["magia_id"] for item in itens_segunda}
    assert magia_bem_n3.id in ids_segunda

    item_n3 = next(item for item in itens_segunda if item["magia_id"] == magia_bem_n3.id)
    assert item_n3["origem"] == "AUTO_NIVEL"


def test_grimorio_limita_magias_conhecidas_bardo_por_nivel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Bardo")
    combatente.nivel = 5  # limite nivel 2 para Bardo = 3
    db.commit()

    magias_n2 = [
        Magia(nome="Bardo N2 A", nivel=2, classe="BARDO", ativo=True, descricao="desc"),
        Magia(nome="Bardo N2 B", nivel=2, classe="BARDO", ativo=True, descricao="desc"),
        Magia(nome="Bardo N2 C", nivel=2, classe="BARDO", ativo=True, descricao="desc"),
        Magia(nome="Bardo N2 D", nivel=2, classe="BARDO", ativo=True, descricao="desc"),
    ]
    db.add_all(magias_n2)
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magias_n2[0].id, classe="BARDO", nivel=2),
        MagiaClasse(magia_id=magias_n2[1].id, classe="BARDO", nivel=2),
        MagiaClasse(magia_id=magias_n2[2].id, classe="BARDO", nivel=2),
        MagiaClasse(magia_id=magias_n2[3].id, classe="BARDO", nivel=2),
    ])
    db.commit()

    client = _build_client(db_factory)

    for magia in magias_n2[:3]:
        resp = client.post(
            f"/api/v1/grimorio/{combatente.id}",
            json={"magia_id": magia.id, "classe": "BARDO", "origem": "SELECAO_MANUAL"},
        )
        assert resp.status_code == 201

    excedente = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magias_n2[3].id, "classe": "BARDO", "origem": "SELECAO_MANUAL"},
    )
    assert excedente.status_code == 409
    assert "Limite de magias conhecidas" in excedente.json()["detail"]


def test_grimorio_bardo_bloqueia_adicao_acima_nivel_conjuravel(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Bardo")
    combatente.nivel = 4  # max conjuravel = 2
    db.commit()

    magia_n3 = Magia(nome="Bardo N3", nivel=3, classe="BARDO", ativo=True, descricao="desc")
    db.add(magia_n3)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_n3.id, classe="BARDO", nivel=3))
    db.commit()

    client = _build_client(db_factory)
    resp = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_n3.id, "classe": "BARDO", "origem": "SELECAO_MANUAL"},
    )

    assert resp.status_code == 400
    assert "nível máximo" in resp.json()["detail"].lower() or "nivel máximo" in resp.json()["detail"].lower()


def test_grimorio_druida_bloqueia_adicao_manual_por_dominio_contrario_ao_alinhamento(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Druida")
    combatente.nivel = 3
    combatente.alinhamento = "Leal e Bom"
    db.commit()

    magia_bloqueada = Magia(
        nome="Druida Dominio Mal",
        nivel=1,
        classe="DRUIDA",
        ativo=True,
        descricao="desc",
        dominios="Mal",
        e_magia_dominio=False,
    )
    db.add(magia_bloqueada)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_bloqueada.id, classe="DRUIDA", nivel=1))
    db.commit()

    client = _build_client(db_factory)
    resp = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_bloqueada.id, "classe": "DRUIDA", "origem": "SELECAO_MANUAL"},
    )

    assert resp.status_code == 400
    assert "alinhamento" in resp.json()["detail"].lower()


def test_grimorio_paladino_bloqueia_adicao_manual_por_dominio_contrario_ao_alinhamento(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Paladino")
    combatente.nivel = 4
    combatente.alinhamento = "Leal e Bom"
    db.commit()

    magia_bloqueada = Magia(
        nome="Paladino Dominio Mal",
        nivel=1,
        classe="PALADINO",
        ativo=True,
        descricao="desc",
        dominios="Mal",
        e_magia_dominio=False,
    )
    db.add(magia_bloqueada)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_bloqueada.id, classe="PALADINO", nivel=1))
    db.commit()

    client = _build_client(db_factory)
    resp = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_bloqueada.id, "classe": "PALADINO", "origem": "SELECAO_MANUAL"},
    )

    assert resp.status_code == 400
    assert "alinhamento" in resp.json()["detail"].lower()


def test_grimorio_clerigo_bloqueia_dominio_oposto_mesmo_nao_sendo_magia_de_dominio(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.dominios = "Bem, Protecao"
    db.commit()

    magia_oposta = Magia(
        nome="Clerigo Dominio Oposto em Magia Base",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Mal",
        e_magia_dominio=False,
    )
    db.add(magia_oposta)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_oposta.id, classe="CLERIGO", nivel=1))
    db.commit()

    client = _build_client(db_factory)
    resp = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_oposta.id, "classe": "CLERIGO", "origem": "SELECAO_MANUAL"},
    )

    assert resp.status_code == 400
    assert "domínio oposto" in resp.json()["detail"].lower() or "dominio oposto" in resp.json()["detail"].lower()


def test_grimorio_clerigo_leal_mau_bloqueia_cura_por_regra_semantica(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.alinhamento = "Leal e Mau"
    combatente.dominios = "Caos, Mal"
    db.commit()

    magia_cura = Magia(
        nome="Cura Leve",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=False,
    )
    db.add(magia_cura)
    db.flush()
    db.add(MagiaClasse(magia_id=magia_cura.id, classe="CLERIGO", nivel=1))
    db.commit()

    client = _build_client(db_factory)
    resp = client.post(
        f"/api/v1/grimorio/{combatente.id}",
        json={"magia_id": magia_cura.id, "classe": "CLERIGO", "origem": "SELECAO_MANUAL"},
    )

    assert resp.status_code == 400
    assert (
        "alinhamento" in resp.json()["detail"].lower()
        or "dominio" in resp.json()["detail"].lower()
    )


@pytest.mark.parametrize(
    "alinhamento,permitidas",
    [
        ("Leal e Bom", {"BEM", "ORDEM"}),
        ("Leal e Neutro", {"ORDEM"}),
        ("Leal e Mau", {"MAL", "ORDEM"}),
        ("Neutro e Bom", {"BEM"}),
        ("Neutro", set()),
        ("Neutro e Mau", {"MAL"}),
        ("Caotico e Bom", {"BEM", "CAOS"}),
        ("Caotico e Neutro", {"CAOS"}),
        ("Caotico e Mau", {"MAL", "CAOS"}),
    ],
)
def test_grimorio_matriz_alinhamento_tendencia_divina(grimorio_db, alinhamento, permitidas):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.alinhamento = alinhamento
    db.commit()

    magias = {
        "BEM": Magia(nome=f"Matriz Bem {alinhamento}", nivel=1, classe="CLERIGO", ativo=True, descricao="desc", dominios="Bem"),
        "MAL": Magia(nome=f"Matriz Mal {alinhamento}", nivel=1, classe="CLERIGO", ativo=True, descricao="desc", dominios="Mal"),
        "ORDEM": Magia(nome=f"Matriz Ordem {alinhamento}", nivel=1, classe="CLERIGO", ativo=True, descricao="desc", dominios="Ordem"),
        "CAOS": Magia(nome=f"Matriz Caos {alinhamento}", nivel=1, classe="CLERIGO", ativo=True, descricao="desc", dominios="Caos"),
    }

    db.add_all(list(magias.values()))
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magias["BEM"].id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magias["MAL"].id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magias["ORDEM"].id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magias["CAOS"].id, classe="CLERIGO", nivel=1),
    ])
    db.commit()

    client = _build_client(db_factory)
    listar = client.get(f"/api/v1/grimorio/{combatente.id}", params={"classe": "CLERIGO"})

    assert listar.status_code == 200
    ids = {item["magia_id"] for item in listar.json()}

    for tendencia, magia in magias.items():
        if tendencia in permitidas:
            assert magia.id in ids
        else:
            assert magia.id not in ids


def test_grimorio_diagnostico_retorna_motivos_de_bloqueio_para_clerigo(grimorio_db):
    db, db_factory = grimorio_db
    combatente = _criar_combatente(db, classe="Clerigo")
    combatente.nivel = 3
    combatente.alinhamento = "Leal e Mau"
    combatente.dominios = "Caos, Mal"
    db.commit()

    magia_cura = Magia(
        nome="Cura Leve",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        e_magia_dominio=False,
    )
    magia_mal = Magia(
        nome="Infligir Ferimentos Leves",
        nivel=1,
        classe="CLERIGO",
        ativo=True,
        descricao="desc",
        dominios="Mal",
        e_magia_dominio=True,
    )
    db.add_all([magia_cura, magia_mal])
    db.flush()
    db.add_all([
        MagiaClasse(magia_id=magia_cura.id, classe="CLERIGO", nivel=1),
        MagiaClasse(magia_id=magia_mal.id, classe="CLERIGO", nivel=1),
    ])
    db.commit()

    client = _build_client(db_factory)
    resp = client.get(
        f"/api/v1/grimorio/{combatente.id}/diagnostico",
        params={"classe": "CLERIGO"},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["classe"] == "CLERIGO"
    assert body["total_magias_avaliadas"] >= 2

    itens = {item["magia_nome"]: item for item in body["itens"]}
    assert "Cura Leve" in itens
    assert "Infligir Ferimentos Leves" in itens

    assert itens["Cura Leve"]["permitida"] is False
    assert "alinhamento" in itens["Cura Leve"]["motivos_bloqueio"]

    assert itens["Infligir Ferimentos Leves"]["permitida"] is True
