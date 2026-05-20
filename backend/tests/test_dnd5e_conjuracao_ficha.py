"""Conjuração persistida na ficha D&D 5e."""

import pytest
from fastapi import HTTPException

from app.games.dnd5e.data.spell_tables import (
    KNOWN_SPELLS_HALF_CASTER,
    magias_preparadas_max_full_caster,
    magias_preparadas_max_paladino,
)
from app.games.dnd5e.models.personagem import Dnd5ePersonagem
from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.repositories.personagem_repository import Dnd5ePersonagemRepository
from app.games.dnd5e.services.conjuracao_ficha_service import (
    Dnd5eConjuracaoFichaService,
)
from app.games.dnd5e.services.conjuracao_shared import magias_conhecidas_max
from app.repositories.base import commit_with_rollback
from app.shared.core.database import SessionLocal


def _conj_svc(db):
    return Dnd5eConjuracaoFichaService(
        Dnd5ePersonagemRepository(db),
        Dnd5eGrimorioRepository(db),
        Dnd5eMagiaRepository(db),
    )


def test_conjuracao_slots_e_descanso_longo():
    db = SessionLocal()
    try:
        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Mago Slots",
            nivel=3,
            intelligence=16,
            ficha_json={"classe_slug": "mago"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        svc = _conj_svc(db)
        estado = svc.obter_estado(p.id)
        assert estado.classe == "mago"
        assert any(s.nivel == 1 and s.total >= 4 for s in estado.slots)

        estado2 = svc.gastar_slot(p.id, 1, 1)
        slot1 = next(s for s in estado2.slots if s.nivel == 1)
        assert slot1.usados == 1

        estado3 = svc.descanso_longo(p.id)
        slot1b = next(s for s in estado3.slots if s.nivel == 1)
        assert slot1b.usados == 0
    finally:
        db.close()


def test_conjuracao_devolver_slot():
    db = SessionLocal()
    try:
        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Mago Devolve",
            nivel=3,
            intelligence=16,
            ficha_json={"classe_slug": "mago"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        svc = _conj_svc(db)

        svc.gastar_slot(p.id, 1, 1)
        estado = svc.devolver_slot(p.id, 1, 1)
        slot1 = next(s for s in estado.slots if s.nivel == 1)
        assert slot1.usados == 0

        with pytest.raises(HTTPException):
            svc.devolver_slot(p.id, 1, 1)
        with pytest.raises(HTTPException):
            svc.devolver_slot(p.id, 99, 1)
    finally:
        db.close()


def test_conjuracao_persiste_magias_lancadas():
    db = SessionLocal()
    try:
        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Mago Lança",
            nivel=3,
            intelligence=16,
            ficha_json={"classe_slug": "mago"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        svc = _conj_svc(db)

        estado = svc.gastar_slot(p.id, 1, 1, magia_id=101)
        assert 101 in estado.magias_lancadas_ids
        slot1 = next(s for s in estado.slots if s.nivel == 1)
        assert slot1.usados == 1

        # Truque (nível 0) não consome slot, mas marca lançada.
        estado2 = svc.gastar_slot(p.id, 0, 1, magia_id=202)
        assert 202 in estado2.magias_lancadas_ids
        # nenhum slot de nível 1 mexido pelo truque
        slot1b = next(s for s in estado2.slots if s.nivel == 1)
        assert slot1b.usados == 1

        # Restaurar magia: remove do set e devolve slot
        estado3 = svc.devolver_slot(p.id, 1, 1, magia_id=101)
        assert 101 not in estado3.magias_lancadas_ids
        slot1c = next(s for s in estado3.slots if s.nivel == 1)
        assert slot1c.usados == 0

        # Descanso longo limpa todas as marcações
        estado4 = svc.descanso_longo(p.id)
        assert estado4.magias_lancadas_ids == []
    finally:
        db.close()


@pytest.mark.parametrize(
    "classe,attr,valor_attr,nivel,esperado",
    [
        ("mago", "intelligence", 16, 3, 6),
        ("mago", "intelligence", 10, 5, 5),
        ("clerigo", "wisdom", 14, 4, 6),
        ("druida", "wisdom", 18, 7, 11),
    ],
)
def test_magias_preparadas_max_full_caster_nao_regride(
    classe, attr, valor_attr, nivel, esperado
):
    db = SessionLocal()
    try:
        kwargs = {
            "tipo": "jogador",
            "nome": f"Prep {classe}",
            "nivel": nivel,
            "ficha_json": {"classe_slug": classe},
        }
        kwargs[attr] = valor_attr
        p = Dnd5ePersonagem(**kwargs)
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        svc = _conj_svc(db)
        estado = svc.obter_estado(p.id)
        assert estado.prepara_magias is True
        assert estado.magias_preparadas_max == esperado
        mod = (valor_attr - 10) // 2
        assert magias_preparadas_max_full_caster(mod, nivel) == esperado
    finally:
        db.close()


def test_paladino_formula_phb():
    assert magias_preparadas_max_paladino(3, 10) == 8
    assert magias_preparadas_max_paladino(0, 2) == 1


def test_patrulheiro_usa_tabela_conhecidas_half_caster():
    assert magias_conhecidas_max("patrulheiro", 6) == KNOWN_SPELLS_HALF_CASTER[6]
    assert magias_conhecidas_max("patrulheiro", 6) == 2
    assert magias_conhecidas_max("mago", 6) is None


def test_paladino_prepara_magias_car_nivel_metade():
    db = SessionLocal()
    try:
        from app.games.dnd5e.models.grimorio import Dnd5eGrimorioMagia
        from app.games.dnd5e.models.magia import Dnd5eMagia

        magia = (
            db.query(Dnd5eMagia)
            .filter(Dnd5eMagia.nivel == 1, Dnd5eMagia.ativo.is_(True))
            .first()
        )
        if not magia:
            magia = Dnd5eMagia(
                slug="paladin-bless-test",
                nome="Bless Paladin Test",
                nivel=1,
                escola="Evocacao",
                ativo=True,
            )
            db.add(magia)
            commit_with_rollback(db)
            db.refresh(magia)

        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Paladino Prep",
            nivel=10,
            charisma=16,
            ficha_json={"classe_slug": "paladino"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        grim = Dnd5eGrimorioRepository(db)
        grim.adicionar(
            Dnd5eGrimorioMagia(
                personagem_id=p.id,
                magia_id=magia.id,
                classe="paladino",
                origem="teste",
            )
        )

        svc = Dnd5eConjuracaoFichaService(
            Dnd5ePersonagemRepository(db), grim, Dnd5eMagiaRepository(db)
        )
        estado = svc.obter_estado(p.id)
        assert estado.prepara_magias is True
        assert estado.magias_preparadas_max == 8  # CAR +3, nível 10 → 3 + 5
        assert estado.magias_conhecidas_max is None

        estado2 = svc.preparar_magias(p.id, [magia.id])
        assert magia.id in estado2.magias_preparadas_ids
    finally:
        db.close()


def test_preparar_magias_mago():
    db = SessionLocal()
    try:
        from app.games.dnd5e.models.grimorio import Dnd5eGrimorioMagia
        from app.games.dnd5e.models.magia import Dnd5eMagia

        magia = (
            db.query(Dnd5eMagia).filter(Dnd5eMagia.slug == "light").first()
            or db.query(Dnd5eMagia).filter(Dnd5eMagia.ativo.is_(True)).first()
        )
        if not magia:
            magia = Dnd5eMagia(
                slug="light-test-prep-unique",
                nome="Light Prep",
                nivel=0,
                escola="Evocacao",
                ativo=True,
            )
            db.add(magia)
            commit_with_rollback(db)
            db.refresh(magia)

        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Mago Prep",
            nivel=3,
            intelligence=16,
            ficha_json={"classe_slug": "mago"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        grim = Dnd5eGrimorioRepository(db)
        grim.adicionar(
            Dnd5eGrimorioMagia(
                personagem_id=p.id,
                magia_id=magia.id,
                classe="mago",
                origem="teste",
            )
        )

        svc = Dnd5eConjuracaoFichaService(
            Dnd5ePersonagemRepository(db), grim, Dnd5eMagiaRepository(db)
        )
        estado = svc.preparar_magias(p.id, [magia.id])
        assert magia.id in estado.magias_preparadas_ids
        assert estado.magias_preparadas_max == 6  # INT +3, nível 3
    finally:
        db.close()


def test_clerigo_prepara_do_catalogo_sem_entrada_previa_no_grimorio():
    db = SessionLocal()
    try:
        from app.games.dnd5e.models.magia import Dnd5eMagia, Dnd5eMagiaClasse

        magia = (
            db.query(Dnd5eMagia)
            .join(Dnd5eMagiaClasse)
            .filter(
                Dnd5eMagiaClasse.classe_slug == "clerigo",
                Dnd5eMagia.nivel == 1,
                Dnd5eMagia.ativo.is_(True),
            )
            .first()
        )
        if not magia:
            pytest.skip("Sem magia de clérigo nível 1 no catálogo")

        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Clerigo Catalogo",
            nivel=5,
            wisdom=16,
            ficha_json={"classe_slug": "clerigo"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        svc = _conj_svc(db)
        estado = svc.preparar_magias(p.id, [magia.id])
        assert magia.id in estado.magias_preparadas_ids
        assert svc.grimorio_repo.obter_item(p.id, magia.id, "clerigo") is not None
    finally:
        db.close()


def test_preparar_truque_nao_conta_no_limite():
    db = SessionLocal()
    try:
        from app.games.dnd5e.models.grimorio import Dnd5eGrimorioMagia
        from app.games.dnd5e.models.magia import Dnd5eMagia

        truque = (
            db.query(Dnd5eMagia)
            .filter(Dnd5eMagia.nivel == 0, Dnd5eMagia.ativo.is_(True))
            .first()
        )
        if not truque:
            pytest.skip("Sem truque no catálogo")

        p = Dnd5ePersonagem(
            tipo="jogador",
            nome="Mago Truque Prep",
            nivel=3,
            intelligence=16,
            ficha_json={"classe_slug": "mago"},
        )
        db.add(p)
        commit_with_rollback(db)
        db.refresh(p)

        grim = Dnd5eGrimorioRepository(db)
        grim.adicionar(
            Dnd5eGrimorioMagia(
                personagem_id=p.id,
                magia_id=truque.id,
                classe="mago",
                origem="teste",
            )
        )

        svc = _conj_svc(db)
        estado = svc.preparar_magias(p.id, [truque.id])
        assert truque.id in estado.magias_preparadas_ids
    finally:
        db.close()
