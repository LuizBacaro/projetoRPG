"""Conjuração avançada na arena — upcast, preparação, concentração."""

import pytest
from fastapi import HTTPException

from app.games.dnd5e.models.grimorio import Dnd5eGrimorioMagia
from app.games.dnd5e.models.magia import Dnd5eMagia
from app.games.dnd5e.repositories.grimorio_repository import Dnd5eGrimorioRepository
from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.schemas.combate import (
    Dnd5eConcentracaoTesteRequest,
    Dnd5eConjurarRequest,
)
from app.games.dnd5e.services.conjuracao_service import Dnd5eConjuracaoService
from app.repositories.base import commit_with_rollback
from app.shared.core.database import SessionLocal
from tests.dnd5e_test_utils import get_or_create_magia


def test_conjurar_upcast_gasta_slot_superior():
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

        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        slots = [0, 4, 3, 2, 0, 0, 0, 0, 0, 0]
        usados = [0] * len(slots)
        res = svc.conjurar(
            Dnd5eConjurarRequest(
                conjurador_id="c1",
                nome="Mago",
                classe="mago",
                nivel_personagem=5,
                magia_id=magia.id,
                mod_inteligencia=3,
                espacos_por_nivel=slots,
                espacos_usados_por_nivel=usados,
                nivel_slot_usado=3,
            )
        )
        assert res.sucesso is True
        assert res.nivel_slot_gasto == 3
        assert res.espacos_usados_por_nivel[3] == 1
    finally:
        db.close()


def test_conjurar_rejeita_nao_preparada():
    db = SessionLocal()
    try:
        magia = get_or_create_magia(
            db, "light", nome="Light", nivel=0, escola="evocacao"
        )

        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        with pytest.raises(HTTPException) as exc:
            svc.conjurar(
                Dnd5eConjurarRequest(
                    conjurador_id="c1",
                    nome="Mago",
                    classe="mago",
                    nivel_personagem=3,
                    magia_id=magia.id,
                    mod_inteligencia=3,
                    validar_preparacao=True,
                    magias_preparadas_ids=[],
                )
            )
        assert "preparada" in str(exc.value.detail).lower()
    finally:
        db.close()


def test_conjurar_ataque_magico_acerto_e_dano():
    db = SessionLocal()
    try:
        magia = get_or_create_magia(
            db,
            "fire-bolt",
            nome="Raio de Fogo",
            nivel=0,
            escola="evocacao",
            dano="1d10",
            ataque_magico="ranged",
        )
        if not magia.ataque_magico or not magia.dano:
            magia.ataque_magico = "ranged"
            magia.dano = magia.dano or "1d10"
            commit_with_rollback(db)

        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        res = svc.conjurar(
            Dnd5eConjurarRequest(
                conjurador_id="c1",
                nome="Mago",
                classe="mago",
                nivel_personagem=5,
                magia_id=magia.id,
                mod_inteligencia=3,
                ac_alvo=12,
                rolagem_ataque_d20=15,
            )
        )
        assert res.sucesso is True
        assert res.ataque_acertou is True
        assert res.dano_total is not None and res.dano_total > 0
    finally:
        db.close()


def test_conjurar_ataque_magico_erro_sem_dano():
    db = SessionLocal()
    try:
        magia = get_or_create_magia(
            db,
            "fire-bolt",
            nome="Raio de Fogo",
            nivel=0,
            escola="evocacao",
            dano="1d10",
            ataque_magico="ranged",
        )

        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        res = svc.conjurar(
            Dnd5eConjurarRequest(
                conjurador_id="c1",
                nome="Mago",
                classe="mago",
                nivel_personagem=5,
                magia_id=magia.id,
                mod_inteligencia=3,
                ac_alvo=20,
                rolagem_ataque_d20=5,
            )
        )
        assert res.sucesso is True
        assert res.ataque_acertou is False
        assert res.dano_total is None
    finally:
        db.close()


def test_conjurar_ritual_nao_gasta_slot():
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
        ritual_antes = bool(magia.ritual)
        magia.ritual = True
        commit_with_rollback(db)

        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        slots = [0, 4, 3, 2, 0, 0, 0, 0, 0, 0]
        usados = [0] * len(slots)
        res = svc.conjurar(
            Dnd5eConjurarRequest(
                conjurador_id="c1",
                nome="Mago",
                classe="mago",
                nivel_personagem=5,
                magia_id=magia.id,
                mod_inteligencia=3,
                espacos_por_nivel=slots,
                espacos_usados_por_nivel=usados,
                como_ritual=True,
            )
        )
        assert res.sucesso is True
        assert res.conjurada_como_ritual is True
        assert res.nivel_slot_gasto is None
        assert res.espacos_usados_por_nivel[3] == 0
        magia.ritual = ritual_antes
        commit_with_rollback(db)
    finally:
        db.close()


def test_conjurar_ritual_rejeita_sem_tag():
    db = SessionLocal()
    try:
        magia = get_or_create_magia(
            db,
            "fireball",
            nome="Fireball",
            nivel=3,
            escola="evocacao",
            ritual=False,
        )
        magia.ritual = False
        commit_with_rollback(db)

        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        with pytest.raises(HTTPException) as exc:
            svc.conjurar(
                Dnd5eConjurarRequest(
                    conjurador_id="c1",
                    nome="Mago",
                    classe="mago",
                    nivel_personagem=5,
                    magia_id=magia.id,
                    mod_inteligencia=3,
                    como_ritual=True,
                )
            )
        assert "ritual" in str(exc.value.detail).lower()
    finally:
        db.close()


def test_conjurar_rejeita_material_nao_confirmado():
    db = SessionLocal()
    try:
        magia = get_or_create_magia(
            db,
            "fireball",
            nome="Fireball",
            nivel=3,
            escola="evocacao",
        )
        consumido_antes = bool(magia.material_consumido)
        material_antes = magia.componentes_material
        magia.material_consumido = True
        magia.componentes_material = "pó de diamante"
        commit_with_rollback(db)

        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        with pytest.raises(HTTPException) as exc:
            svc.conjurar(
                Dnd5eConjurarRequest(
                    conjurador_id="c1",
                    nome="Mago",
                    classe="mago",
                    nivel_personagem=5,
                    magia_id=magia.id,
                    mod_inteligencia=3,
                    confirmar_material_consumido=False,
                )
            )
        assert "consumo" in str(exc.value.detail).lower()
        magia.material_consumido = consumido_antes
        magia.componentes_material = material_antes
        commit_with_rollback(db)
    finally:
        db.close()


def test_conjurar_salvaguarda_metade_dano_no_sucesso():
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
        magia.teste_resistencia = "dex"
        magia.dano = magia.dano or "8d6"
        commit_with_rollback(db)

        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        slots = [0, 4, 3, 2, 0, 0, 0, 0, 0, 0]
        res = svc.conjurar(
            Dnd5eConjurarRequest(
                conjurador_id="c1",
                nome="Mago",
                classe="mago",
                nivel_personagem=5,
                magia_id=magia.id,
                mod_inteligencia=3,
                espacos_por_nivel=slots,
                espacos_usados_por_nivel=[0] * len(slots),
                teste_resistencia_mod_alvo=5,
                rolagem_salvaguarda_alvo=20,
            )
        )
        assert res.sucesso is True
        assert res.salvaguarda_passou is True
        assert res.dano_total is not None and res.dano_total > 0
        assert res.dano_aplicar == res.dano_total // 2
    finally:
        db.close()


def test_concentracao_perdida_em_dano_alto():
    db = SessionLocal()
    try:
        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        res = svc.teste_concentracao(
            Dnd5eConcentracaoTesteRequest(
                conjurador_id="c1",
                dano_recebido=50,
                mod_constituicao=0,
                bonus_proficiencia=2,
                magia_concentracao_id=42,
                rolagem_d20=1,
            )
        )
        assert res.manteve_concentracao is False
        assert res.dc == 25
        assert res.magia_concentracao_id is None
    finally:
        db.close()
