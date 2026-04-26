import json

from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.combatentes import router as combatentes_router
from app.core.database import Base, get_db
from app.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.games.dnd35.models.armadura_protecao import ArmaduraProtecao, ArmaduraProtecaoJogador
from app.games.dnd35.models.talento import Talento, TalentoJogador


class _UsuarioDummy:
    def __init__(self, user_id: int):
        self.id = user_id


@pytest.fixture(scope="function")
def combatentes_db():
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
    app.include_router(combatentes_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: _UsuarioDummy(77)
    app.dependency_overrides[requer_dono_ou_admin_combatente] = lambda: object()

    return TestClient(app)


def _combatente_payload(**overrides):
    payload = {
        "nome": "Irmão Aldren",
        "tipo": "jogador",
        "classe": "Clérigo",
        "raca": "Humano",
        # St. Cuthbert (Tabela 3-7): Destruição, Ordem, Proteção, Força
        "divindade": "St. Cuthbert",
        "alinhamento": "Leal e Bom",
        "dominios": "Proteção, Força",
        "hp_maximo": "18",
        "iniciativa": "1",
        "ca": "16",
        "toque": "11",
        "surpresa": "15",
        "forca": "10",
        "destreza": "12",
        "constituicao": "14",
        "inteligencia": "10",
        "sabedoria": "17",
        "carisma": "13",
        "fortitude": "4",
        "reflexos": "1",
        "vontade": "6",
        "nivel": "5",
        "pontos": "0",
    }
    payload.update(overrides)
    return payload


def test_criar_combatente_retorna_alinhamento_e_dominios(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    response = client.post("/api/v1/combatentes", data=_combatente_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["dono_id"] == 77
    assert body["divindade"] == "St. Cuthbert"
    assert body["alinhamento"] == "Leal e Bom"
    assert body["dominios"] == "Proteção, Força"
    assert body["hp_atual"] == 18
    assert body["pc"] == 0
    assert body["pp"] == 0
    assert body["po"] == 0
    assert body["pl"] == 0


def test_criar_combatente_rejeita_divindade_incompativel_com_alinhamento(combatentes_db):
    """Regra do 1-passo: Leal e Bom não pode escolher Gruumsh (Caótico e Mau)."""
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    payload = _combatente_payload(
        divindade="Gruumsh",
        alinhamento="Leal e Bom",
        dominios="Proteção, Força",
    )
    response = client.post("/api/v1/combatentes", data=payload)

    assert response.status_code == 400
    detalhe = response.json().get("detail", "")
    assert "alinhamento" in detalhe.lower()
    assert "gruumsh" in detalhe.lower()


def test_criar_combatente_rejeita_dominio_alinhamental_conflitante(combatentes_db):
    """Clérigo Leal e Bom não pode ter o domínio Mal.

    Usamos uma divindade fora do catálogo (Tabela 3-7) para isolar a
    validação: a divindade em si não impõe lista de domínios, mas a regra
    alinhamental bloqueia o clérigo "Leal e Bom" de tomar Mal/Caos.
    """
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    payload = _combatente_payload(
        divindade="Deusa Caseira da Campanha",  # não catalogada
        alinhamento="Leal e Bom",
        dominios="Mal, Ordem",
    )
    response = client.post("/api/v1/combatentes", data=payload)

    assert response.status_code == 400
    detalhe = response.json().get("detail", "")
    assert "mal" in detalhe.lower()
    assert "alinhamento" in detalhe.lower()


def test_atualizar_combatente_persiste_campos_dinheiro(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    criado = client.post("/api/v1/combatentes", data=_combatente_payload())
    assert criado.status_code == 201
    combatente_id = criado.json()["id"]

    atualizar = client.put(
        f"/api/v1/combatentes/{combatente_id}",
        data=_combatente_payload(pc="11", pp="22", po="33", pl="44"),
    )
    assert atualizar.status_code == 200
    body = atualizar.json()
    assert body["pc"] == 11
    assert body["pp"] == 22
    assert body["po"] == 33
    assert body["pl"] == 44


def test_atualizar_combatente_persiste_alinhamento_e_dominios_editados(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    criado = client.post("/api/v1/combatentes", data=_combatente_payload())
    combatente_id = criado.json()["id"]

    atualizar = client.put(
        f"/api/v1/combatentes/{combatente_id}",
        data=_combatente_payload(
            # Wee Jas (Tabela 3-7): Morte, Ordem, Magia
            divindade="Wee Jas",
            alinhamento="Neutro e Bom",
            dominios="Morte, Magia",
            sabedoria="18",
        ),
    )

    assert atualizar.status_code == 200
    body = atualizar.json()
    assert body["divindade"] == "Wee Jas"
    assert body["alinhamento"] == "Neutro e Bom"
    assert body["dominios"] == "Morte, Magia"
    assert body["sabedoria"] == 18

    obter = client.get(f"/api/v1/combatentes/{combatente_id}")

    assert obter.status_code == 200
    assert obter.json()["divindade"] == "Wee Jas"
    assert obter.json()["alinhamento"] == "Neutro e Bom"
    assert obter.json()["dominios"] == "Morte, Magia"


def test_aplicar_dano_massa_sucesso(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    c1 = client.post("/api/v1/combatentes", data=_combatente_payload(nome="Aldren"))
    c2 = client.post("/api/v1/combatentes", data=_combatente_payload(nome="Borin"))
    ids = [c1.json()["id"], c2.json()["id"]]

    response = client.post(
        "/api/v1/combatentes/dano/massa",
        json={"combatente_ids": ids, "valor": 5},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["resultados"]) == 2
    assert {item["id"] for item in body["resultados"]} == set(ids)
    assert all(item["hp_atual"] == 13 for item in body["resultados"])


def test_aplicar_cura_massa_sucesso(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    c1 = client.post("/api/v1/combatentes", data=_combatente_payload(nome="Aldren"))
    c2 = client.post("/api/v1/combatentes", data=_combatente_payload(nome="Borin"))
    ids = [c1.json()["id"], c2.json()["id"]]

    client.post(
        "/api/v1/combatentes/dano/massa",
        json={"combatente_ids": ids, "valor": 7},
    )

    response = client.post(
        "/api/v1/combatentes/cura/massa",
        json={"combatente_ids": ids, "valor": 3},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["resultados"]) == 2
    assert {item["id"] for item in body["resultados"]} == set(ids)
    assert all(item["hp_atual"] == 14 for item in body["resultados"])


def test_criar_combatente_preenche_bonus_base_ataque_por_classe_e_nivel(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    response = client.post(
        "/api/v1/combatentes",
        data=_combatente_payload(classe="Guerreiro", nivel="6"),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["bonus_base_ataque"] == "+6/+1"
    assert "Talento Adicional" in (body.get("habilidades_especiais") or "")
    assert body["fortitude_base"] == 5
    assert body["reflexos_base"] == 2
    assert body["vontade_base"] == 2
    assert body["fortitude"] == 7
    assert body["reflexos"] == 3
    assert body["vontade"] == 5


def test_defesas_sao_recalculadas_automaticamente_por_destreza_e_armadura(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    # DES 14 => mod +2. Sem armadura explícita na criação, bônus de armadura = 0.
    response = client.post(
        "/api/v1/combatentes",
        data=_combatente_payload(
            classe="Guerreiro",
            nivel="4",
            destreza="14",
        ),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["toque"] == 12      # 10 + mod DES
    assert body["surpresa"] == 10   # 10 + bônus de armadura (inicialmente 0)
    assert body["ca"] == 12         # 10 + mod DES + bônus de armadura (0)


def test_defesas_usam_bonus_ca_de_armadura_item_protecao(combatentes_db):
    db, db_factory = combatentes_db
    client = _build_client(db_factory)

    criado = client.post(
        "/api/v1/combatentes",
        data=_combatente_payload(
            classe="Guerreiro",
            nivel="4",
            destreza="14",  # mod +2
        ),
    )
    assert criado.status_code == 201
    combatente_id = criado.json()["id"]

    item = ArmaduraProtecao(
        nome="Cota de Malha + Escudo",
        tipo="Armadura",
        bonus_ca=6,
        ativo=True,
    )
    db.add(item)
    db.flush()
    db.add(ArmaduraProtecaoJogador(combatente_id=combatente_id, item_id=item.id))
    db.commit()

    obter = client.get(f"/api/v1/combatentes/{combatente_id}")
    assert obter.status_code == 200
    body = obter.json()
    assert body["toque"] == 12      # 10 + mod DES
    assert body["surpresa"] == 16   # 10 + bônus de armadura (item)
    assert body["ca"] == 18         # 10 + mod DES + bônus de armadura


def test_habilidades_especiais_incluem_todos_os_niveis_ate_o_atual(combatentes_db):
    """Coluna Especial: acumula linhas do 1° ao nível do personagem (não só o nível atual)."""
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    response = client.post(
        "/api/v1/combatentes",
        data=_combatente_payload(classe="Guerreiro", nivel="6"),
    )
    assert response.status_code == 201
    raw = response.json().get("habilidades_especiais") or ""
    grupos = json.loads(raw)
    assert isinstance(grupos, list)
    niveis = {item["nivel"] for item in grupos if isinstance(item, dict)}
    # Catálogo Guerreiro: talentos em 1°, 2°, 4° e 6°; 3° e 5° são "-"
    assert niveis == {1, 2, 4, 6}


def test_atualizar_combatente_recalcula_bonus_base_ataque_quando_classe_ou_nivel_mudam(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    criado = client.post(
        "/api/v1/combatentes",
        data=_combatente_payload(classe="Bardo", nivel="8"),
    )
    assert criado.status_code == 201
    combatente_id = criado.json()["id"]
    assert criado.json()["bonus_base_ataque"] == "+6/+1"

    atualizado = client.put(
        f"/api/v1/combatentes/{combatente_id}",
        data=_combatente_payload(classe="Mago", nivel="8"),
    )
    assert atualizado.status_code == 200
    assert atualizado.json()["bonus_base_ataque"] == "+4"
    habilidades = atualizado.json().get("habilidades_especiais") or ""
    assert isinstance(habilidades, str)
    assert atualizado.json()["fortitude_base"] == 2
    assert atualizado.json()["reflexos_base"] == 2
    assert atualizado.json()["vontade_base"] == 6
    assert atualizado.json()["fortitude"] == 4
    assert atualizado.json()["reflexos"] == 3
    assert atualizado.json()["vontade"] == 9


def test_jogador_com_iniciativa_aprimorada_recebe_bonus_na_iniciativa(combatentes_db):
    db, db_factory = combatentes_db
    client = _build_client(db_factory)

    criado = client.post(
        "/api/v1/combatentes",
        data=_combatente_payload(classe="Guerreiro", nivel="4", destreza="14"),
    )
    assert criado.status_code == 201
    combatente_id = criado.json()["id"]

    talento = Talento(nome="Iniciativa Aprimorada", descricao="+4 em iniciativa", ativo=True)
    db.add(talento)
    db.flush()
    db.add(TalentoJogador(combatente_id=combatente_id, talento_id=talento.id))
    db.commit()

    obter = client.get(f"/api/v1/combatentes/{combatente_id}")
    assert obter.status_code == 200
    body = obter.json()
    # DES 14 => +2; Iniciativa Aprimorada => +4; total esperado = +6
    assert body["iniciativa"] == 6


def test_criar_combatente_aplica_predefinicoes_raciais_basicas(combatentes_db):
    _, db_factory = combatentes_db
    client = _build_client(db_factory)

    response = client.post(
        "/api/v1/combatentes",
        data=_combatente_payload(
            raca="Elfos",
            forca="10",
            destreza="10",
            constituicao="10",
            inteligencia="10",
            sabedoria="10",
            carisma="10",
        ),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["raca"] == "Elfos"
    assert body["raca_slug"] == "elfos"
    assert body["destreza"] == 12
    assert body["constituicao"] == 8
    assert body["tamanho_racial"] == "Médio"
    assert body["deslocamento_racial_metros"] == 9
    assert "Comum" in body["idiomas_raciais"]
    assert isinstance(body["passivos_raciais"], list)