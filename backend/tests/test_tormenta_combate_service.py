"""Serviço de combate Tormenta (Arena) — ordenação e ciclo básico."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.games.tormenta.models.personagem import TormentaPersonagem
from app.games.tormenta.repositories.combate_repository import TormentaCombateRepository
from app.games.tormenta.repositories.personagem_repository import TormentaPersonagemRepository
from app.games.tormenta.services.combate_service import TormentaCombateService
from app.shared.core.database import Base
from app.shared.core.security import hash_senha
from app.shared.exceptions.custom_exceptions import CombateJaAtivoError
from app.shared.models.usuario import PerfilUsuario, Usuario as UModel


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
    a = TormentaPersonagem(dono_id=u.id, tipo="monstro", nome="A", iniciativa=1, ficha_json={})
    b = TormentaPersonagem(dono_id=u.id, tipo="monstro", nome="B", iniciativa=2, ficha_json={})
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
    a = TormentaPersonagem(dono_id=u.id, tipo="monstro", nome="A", iniciativa=2, ficha_json={})
    b = TormentaPersonagem(dono_id=u.id, tipo="monstro", nome="B", iniciativa=1, ficha_json={})
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
