"""Conjuração persistida na ficha D&D 5e."""

from app.games.dnd5e.models.personagem import Dnd5ePersonagem
from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.personagem_repository import Dnd5ePersonagemRepository
from app.games.dnd5e.services.conjuracao_ficha_service import Dnd5eConjuracaoFichaService
from app.repositories.base import commit_with_rollback
from app.shared.core.database import SessionLocal


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

        svc = Dnd5eConjuracaoFichaService(
            Dnd5ePersonagemRepository(db), Dnd5eGrimorioRepository(db)
        )
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
            Dnd5ePersonagemRepository(db), grim
        )
        estado = svc.preparar_magias(p.id, [magia.id])
        assert magia.id in estado.magias_preparadas_ids
        assert estado.magias_preparadas_max == 6  # INT +3, nível 3
    finally:
        db.close()
