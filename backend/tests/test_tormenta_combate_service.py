"""Serviço de combate Tormenta (Arena) — ordenação e ciclo básico."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.repositories.combate_repository import TormentaCombateRepository
from app.games.tormenta.repositories.personagem_repository import (
    TormentaPersonagemRepository,
)
from app.games.tormenta.schemas.combate import TormentaCombateCondicaoMbItem
from app.games.tormenta.services.combate_service import TormentaCombateService
from app.shared.core.database import Base
from app.shared.core.security import hash_senha
from app.shared.exceptions.custom_exceptions import CombateJaAtivoError, DadosInvalidos
from app.shared.models.usuario import PerfilUsuario
from app.shared.models.usuario import Usuario as UModel


@pytest.fixture
def db_tormenta_combate():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        u = UModel(
            perfil=PerfilUsuario.MESTRE,
            nome="Mestre Arena T20",
            email="mestre.t20.combate@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add(u)
        db.commit()
        db.refresh(u)
        yield db, u
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def test_iniciar_ordena_por_iniciativa_e_empate_nome(db_tormenta_combate):
    db, u = db_tormenta_combate
    p_ini10_b = TormentaPersonagem(
        dono_id=u.id,
        tipo="monstro",
        nome="Bruxo",
        iniciativa=10,
        ficha_json={},
    )
    p_ini10_a = TormentaPersonagem(
        dono_id=u.id,
        tipo="monstro",
        nome="Aranha",
        iniciativa=10,
        ficha_json={},
    )
    p_ini15 = TormentaPersonagem(
        dono_id=u.id,
        tipo="monstro",
        nome="Zumbi",
        iniciativa=15,
        ficha_json={},
    )
    db.add_all([p_ini10_b, p_ini10_a, p_ini15])
    db.commit()
    for p in (p_ini10_b, p_ini10_a, p_ini15):
        db.refresh(p)

    svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([p_ini10_b.id, p_ini10_a.id, p_ini15.id])
    st = svc.obter_status_combate()
    assert st["ativo"] is True
    # Maior iniciativa primeiro; empate: nome pt-BR (aranha antes de bruxo).
    assert st["personagens_ids"] == [p_ini15.id, p_ini10_a.id, p_ini10_b.id]


def test_nao_permite_dois_combates_ativos(db_tormenta_combate):
    db, u = db_tormenta_combate
    a = TormentaPersonagem(
        dono_id=u.id, tipo="monstro", nome="A", iniciativa=1, ficha_json={}
    )
    b = TormentaPersonagem(
        dono_id=u.id, tipo="monstro", nome="B", iniciativa=2, ficha_json={}
    )
    db.add_all([a, b])
    db.commit()
    db.refresh(a)
    db.refresh(b)

    svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([a.id, b.id])
    with pytest.raises(CombateJaAtivoError):
        svc.iniciar_combate([b.id, a.id])


def test_avancar_turno_e_finalizar(db_tormenta_combate):
    db, u = db_tormenta_combate
    a = TormentaPersonagem(
        dono_id=u.id, tipo="monstro", nome="A", iniciativa=2, ficha_json={}
    )
    b = TormentaPersonagem(
        dono_id=u.id, tipo="monstro", nome="B", iniciativa=1, ficha_json={}
    )
    db.add_all([a, b])
    db.commit()
    db.refresh(a)
    db.refresh(b)

    svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([a.id, b.id])
    assert svc.obter_status_combate()["turno_atual"] == 0
    svc.avancar_turno()
    assert svc.obter_status_combate()["turno_atual"] == 1
    svc.avancar_turno()
    st = svc.obter_status_combate()
    assert st["turno_atual"] == 0
    assert st["rodada_atual"] == 2
    svc.finalizar_combate()
    assert svc.obter_status_combate()["ativo"] is False


def test_condicoes_mb_persistem_no_combate(db_tormenta_combate):
    db, u = db_tormenta_combate
    a = TormentaPersonagem(
        dono_id=u.id, tipo="monstro", nome="A", iniciativa=2, ficha_json={}
    )
    b = TormentaPersonagem(
        dono_id=u.id, tipo="monstro", nome="B", iniciativa=1, ficha_json={}
    )
    db.add_all([a, b])
    db.commit()
    db.refresh(a)
    db.refresh(b)

    svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([a.id, b.id])

    svc.aplicar_condicoes_mb(
        {
            str(a.id): TormentaCombateCondicaoMbItem(
                rotulos=["Assustado"], tips=["tip-a"]
            ),
            str(b.id): TormentaCombateCondicaoMbItem(rotulos=["Caído"], tips=["tip-b"]),
        }
    )
    st = svc.obter_status_combate()
    cm = st.get("condicoes_mb") or {}
    assert cm[str(a.id)]["rotulos"] == ["Assustado"]
    assert cm[str(b.id)]["tips"] == ["tip-b"]

    svc.aplicar_condicoes_mb(
        {str(a.id): TormentaCombateCondicaoMbItem(rotulos=[], tips=[])}
    )
    st2 = svc.obter_status_combate()
    cm2 = st2.get("condicoes_mb") or {}
    assert str(a.id) not in cm2
    assert cm2[str(b.id)]["rotulos"] == ["Caído"]


def test_rolar_iniciativa_v13_usa_valor_des(db_tormenta_combate):
    db, u = db_tormenta_combate
    p = TormentaPersonagem(
        dono_id=u.id,
        tipo="jogador",
        nome="Agil",
        des_valor=2,
        iniciativa=0,
        ficha_json={"regra_versao": "v13"},
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([p.id])
    out = svc.rolar_iniciativa_combate([p.id])
    r0 = out["resultados"][0]
    assert r0["modificador"] == 2
    assert r0["total"] == r0["d20"] + 2


def test_aplicar_iniciativa_manual_reordena_combate(db_tormenta_combate):
    db, u = db_tormenta_combate
    rapido = TormentaPersonagem(
        dono_id=u.id,
        tipo="jogador",
        nome="Zara",
        iniciativa=0,
        ficha_json={},
    )
    lento = TormentaPersonagem(
        dono_id=u.id,
        tipo="monstro",
        nome="Orc",
        iniciativa=0,
        ficha_json={},
    )
    db.add_all([rapido, lento])
    db.commit()
    db.refresh(rapido)
    db.refresh(lento)

    svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([lento.id, rapido.id])
    out = svc.aplicar_iniciativa_manual({str(lento.id): 8, str(rapido.id): 19})
    assert out["ordem"] == [rapido.id, lento.id]
    assert out["resultados"][0]["total"] == 19
    st = svc.obter_status_combate()
    assert st["personagens_ids"] == [rapido.id, lento.id]
    assert st["turno_atual"] == 0


def test_aplicar_iniciativa_manual_exige_todos_combatentes(db_tormenta_combate):
    db, u = db_tormenta_combate
    a = TormentaPersonagem(dono_id=u.id, tipo="jogador", nome="A", ficha_json={})
    b = TormentaPersonagem(dono_id=u.id, tipo="jogador", nome="B", ficha_json={})
    db.add_all([a, b])
    db.commit()
    db.refresh(a)
    db.refresh(b)

    svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([a.id, b.id])
    with pytest.raises(DadosInvalidos):
        svc.aplicar_iniciativa_manual({str(a.id): 12})


def test_rolar_ataque_usa_ca_com_armaduras_ficha(db_tormenta_combate):
    db, u = db_tormenta_combate
    alvo = TormentaPersonagem(
        dono_id=u.id,
        tipo="jogador",
        nome="Tank",
        des_valor=2,
        ca=12,
        ficha_json={
            "regra_versao": "v13",
            "armaduras_protecao": [
                {"nome": "Couro", "tipo": "leve", "bonus_ca": 2},
                {"nome": "Broquel", "tipo": "escudo", "bonus_ca": 1, "empunhado": True},
            ],
        },
    )
    atk = TormentaPersonagem(
        dono_id=u.id,
        tipo="monstro",
        nome="Goblin",
        ficha_json={},
    )
    db.add_all([alvo, atk])
    db.commit()
    db.refresh(alvo)
    db.refresh(atk)

    svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([atk.id, alvo.id])
    roll = svc.rolar_ataque_combate(
        atacante_id=atk.id,
        alvo_id=alvo.id,
        bab=0,
        mod_atributo=0,
    )
    assert roll["ca_alvo"] == 15
    st = svc.obter_status_combate()
    pers = {p["id"]: p for p in st["personagens"]}
    assert pers[alvo.id]["ca"] == 15
    assert pers[alvo.id]["ca_efetiva"] == 15


def test_rolar_ataque_aplica_condicao_desprevenido_no_alvo(db_tormenta_combate):
    db, u = db_tormenta_combate
    alvo = TormentaPersonagem(
        dono_id=u.id,
        tipo="jogador",
        nome="Desp",
        des_valor=0,
        ca=10,
        ficha_json={"regra_versao": "v13"},
    )
    atk = TormentaPersonagem(
        dono_id=u.id,
        tipo="monstro",
        nome="Goblin",
        ficha_json={},
    )
    db.add_all([alvo, atk])
    db.commit()
    db.refresh(alvo)
    db.refresh(atk)

    svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([atk.id, alvo.id])
    svc.aplicar_condicoes_mb(
        {
            str(alvo.id): TormentaCombateCondicaoMbItem(
                rotulos=["Desprevenido"],
                tips=["−5 Defesa"],
            ),
        }
    )
    roll = svc.rolar_ataque_combate(
        atacante_id=atk.id,
        alvo_id=alvo.id,
        bab=0,
        mod_atributo=0,
    )
    assert roll["ca_base_alvo"] == 10
    assert roll["modificador_condicoes_ca_alvo"] == -5
    assert roll["ca_alvo"] == 5


def test_status_finaliza_combate_orfao_automaticamente(db_tormenta_combate):
    from app.games.tormenta.models.combate import TormentaCombate

    db, u = db_tormenta_combate
    combate_repo = TormentaCombateRepository(db)
    combate_repo.create(
        TormentaCombate(
            usuario_id=u.id,
            personagens_ids=[99999],
            turno_atual=0,
            rodada_atual=1,
            ativo=True,
            condicoes_mb_json={},
        )
    )

    svc = TormentaCombateService(
        combate_repo,
        TormentaPersonagemRepository(db),
        u.id,
    )
    st = svc.obter_status_combate()
    assert st["ativo"] is False
    assert combate_repo.get_ativo_por_usuario(u.id) is None


def test_iniciar_combate_apos_orfao_permite_novo(db_tormenta_combate):
    from app.games.tormenta.models.combate import TormentaCombate

    db, u = db_tormenta_combate
    combate_repo = TormentaCombateRepository(db)
    combate_repo.create(
        TormentaCombate(
            usuario_id=u.id,
            personagens_ids=[99999],
            turno_atual=0,
            rodada_atual=1,
            ativo=True,
            condicoes_mb_json={},
        )
    )
    p = TormentaPersonagem(
        dono_id=u.id, tipo="monstro", nome="Goblin", iniciativa=3, ficha_json={}
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    svc = TormentaCombateService(
        combate_repo,
        TormentaPersonagemRepository(db),
        u.id,
    )
    svc.iniciar_combate([p.id])
    st = svc.obter_status_combate()
    assert st["ativo"] is True
    assert st["personagens_ids"] == [p.id]


def test_excluir_personagem_finaliza_combate_orfao(db_tormenta_combate):
    from app.games.tormenta.services.personagem_service import TormentaPersonagemService

    db, u = db_tormenta_combate
    p = TormentaPersonagem(
        dono_id=u.id, tipo="monstro", nome="NPC", iniciativa=1, ficha_json={}
    )
    db.add(p)
    db.commit()
    db.refresh(p)

    combate_svc = TormentaCombateService(
        TormentaCombateRepository(db),
        TormentaPersonagemRepository(db),
        u.id,
    )
    combate_svc.iniciar_combate([p.id])

    personagem_svc = TormentaPersonagemService(TormentaPersonagemRepository(db))
    personagem_svc.excluir(p.id)

    st = combate_svc.obter_status_combate()
    assert st["ativo"] is False
    assert TormentaCombateRepository(db).get_ativo_por_usuario(u.id) is None
