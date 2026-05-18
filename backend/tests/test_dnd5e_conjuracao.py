"""Conjuração na arena D&D 5e."""

import pytest
from fastapi import HTTPException

from app.games.dnd5e.models.magia import Dnd5eMagia, Dnd5eMagiaClasse
from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.schemas.combate import Dnd5eConjurarRequest
from app.games.dnd5e.services.conjuracao_service import Dnd5eConjuracaoService
from app.repositories.base import commit_with_rollback
from app.shared.core.database import SessionLocal
from tests.dnd5e_test_utils import get_or_create_magia


def test_conjurar_truque_gasta_sem_slot():
    db = SessionLocal()
    try:
        magia = get_or_create_magia(
            db,
            "light",
            nome="Light",
            nivel=0,
            escola="evocacao",
            componentes_verbal=True,
        )

        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        res = svc.conjurar(
            Dnd5eConjurarRequest(
                conjurador_id="c1",
                nome="Mago",
                classe="mago",
                nivel_personagem=3,
                magia_id=magia.id,
                mod_inteligencia=3,
            )
        )
        assert res.sucesso is True
        assert res.dc == 8 + 2 + 3
    finally:
        db.close()


def test_conjurar_exige_grimorio_quando_personagem_id():
    db = SessionLocal()
    try:
        magia = get_or_create_magia(
            db,
            "fireball",
            nome="Fireball",
            nivel=3,
            escola="evocacao",
            dano="8d6",
            teste_resistencia="dex",
        )

        svc = Dnd5eConjuracaoService(
            Dnd5eMagiaRepository(db), Dnd5eGrimorioRepository(db)
        )
        with pytest.raises(HTTPException) as exc:
            svc.conjurar(
                Dnd5eConjurarRequest(
                    conjurador_id="c1",
                    nome="Mago",
                    classe="mago",
                    nivel_personagem=5,
                    magia_id=magia.id,
                    personagem_id=99999,
                    mod_inteligencia=3,
                    espacos_por_nivel=[0, 4, 3, 2, 0, 0, 0, 0, 0, 0],
                )
            )
        assert "grimório" in str(exc.value.detail).lower()
    finally:
        db.close()
