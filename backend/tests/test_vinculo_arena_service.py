"""Testes de inclusão de vínculos na arena."""

from types import SimpleNamespace

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.games.dnd35.models.combatente import Combatente
from app.games.dnd35.models.companheiro_animal import CompanheiroAnimal
from app.games.dnd35.models.familiar import Familiar
from app.games.dnd35.repositories.combatente_repository import CombatenteRepository
from app.games.dnd35.repositories.companheiro_animal_repository import (
    CompanheiroAnimalRepository,
)
from app.games.dnd35.repositories.familiar_repository import FamiliarRepository
from app.games.dnd35.services.vinculo_arena_service import VinculoArenaService
from app.shared.core.database import Base


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = Session()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _druida(db):
    c = Combatente(
        nome="Druida Teste",
        tipo="jogador",
        classe="Druida",
        raca="Humano",
        nivel=7,
        forca=10,
        destreza=14,
        constituicao=10,
        inteligencia=10,
        sabedoria=10,
        carisma=10,
        hp_atual=40,
        hp_maximo=40,
        iniciativa=12,
    )
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def test_expandir_ids_com_companheiro(db_session):
    mestre = _druida(db_session)
    ca = CompanheiroAnimal(
        combatente_id=mestre.id,
        especie_slug="lobo",
        nome="Greywind",
        forca=12,
        destreza=14,
        constituicao=12,
        inteligencia=2,
        sabedoria=12,
        carisma=6,
        hp_atual=20,
        hp_maximo=20,
        ca=14,
    )
    db_session.add(ca)
    db_session.commit()

    svc = VinculoArenaService(
        db_session,
        combatente_repo=CombatenteRepository(db_session),
        companheiro_repo=CompanheiroAnimalRepository(db_session),
        familiar_repo=FamiliarRepository(db_session),
    )
    ids = svc.expandir_combatente_ids([mestre.id], incluir_vinculos=True)
    assert len(ids) == 2
    assert mestre.id in ids
    npc_id = [i for i in ids if i != mestre.id][0]
    npc = db_session.get(Combatente, npc_id)
    assert npc is not None
    assert npc.tipo == "npc"
    assert npc.nome == "Greywind"


def test_expandir_ids_com_familiar(db_session):
    mestre = Combatente(
        nome="Mago Teste",
        tipo="jogador",
        classe="Mago",
        raca="Humano",
        nivel=5,
        forca=10,
        destreza=12,
        constituicao=10,
        inteligencia=16,
        sabedoria=10,
        carisma=10,
        hp_atual=20,
        hp_maximo=20,
        iniciativa=8,
    )
    db_session.add(mestre)
    db_session.commit()
    db_session.refresh(mestre)

    fam = Familiar(
        combatente_id=mestre.id,
        especie_slug="coruja",
        nome="Hoot",
        nivel_mestre=5,
        inteligencia=7,
        armadura_natural_bonus=2,
        hp_atual=10,
        hp_maximo=10,
        ca=14,
        bonus_mestre="+3 em testes de Escutar",
    )
    db_session.add(fam)
    db_session.commit()

    svc = VinculoArenaService(
        db_session,
        combatente_repo=CombatenteRepository(db_session),
        companheiro_repo=CompanheiroAnimalRepository(db_session),
        familiar_repo=FamiliarRepository(db_session),
    )
    ids = svc.expandir_combatente_ids([mestre.id], incluir_vinculos=True)
    assert len(ids) == 2
    npc = db_session.get(Combatente, ids[1])
    assert npc.classe == "Familiar"
