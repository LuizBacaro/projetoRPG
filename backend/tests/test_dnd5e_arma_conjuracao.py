"""Propriedades de arma e conjuração com armadura."""

import pytest
from fastapi import HTTPException

from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.rules.arma_combate import (
    calcular_dano_com_arma,
    mod_atributo_para_arma,
    resolver_ataque_com_arma,
)
from app.games.dnd5e.rules.conjuracao_armadura import validar_conjuracao_armadura
from app.games.dnd5e.rules.equipamento import arma_por_slug
from app.games.dnd5e.schemas.combate import Dnd5eConjurarRequest
from app.games.dnd5e.services.conjuracao_service import Dnd5eConjuracaoService
from app.shared.core.database import SessionLocal
from tests.dnd5e_test_utils import get_or_create_magia


def test_finesse_usa_maior_str_ou_dex():
    adaga = arma_por_slug("adaga")
    mod, attr = mod_atributo_para_arma(adaga, str_mod=1, dex_mod=3)
    assert mod == 3
    assert attr == "dexterity"


def test_versatil_duas_maos_aumenta_dado():
    res = calcular_dano_com_arma(
        arma_slug="espada-longa",
        str_mod=3,
        dex_mod=1,
        duas_maos=True,
        rng=lambda a, b: 6,
    )
    assert res["expressao_dano"] == "1d10"
    assert res["dano_total"] >= 4


def test_resolver_ataque_adaga_finesse():
    r = resolver_ataque_com_arma(
        arma_slug="adaga",
        str_mod=1,
        dex_mod=4,
        bonus_proficiencia=2,
        ac_alvo=12,
        rolagem_d20=15,
    )
    assert r["acerto"] is True
    assert r["mod_atributo_usado"] == 4
    assert "finesse" in r["propriedades"]


def test_mago_sem_proficiencia_armadura_pesada():
    ok, msg = validar_conjuracao_armadura("mago", armadura_slug="cota-anéis")
    assert ok is False
    assert "bloqueada" in msg.lower()


def test_clerigo_pode_armadura_media():
    ok, _ = validar_conjuracao_armadura("clerigo", armadura_slug="brunea")
    assert ok is True


def test_conjurar_bloqueia_mago_com_armadura():
    db = SessionLocal()
    try:
        magia = get_or_create_magia(
            db, "light-armor-test", nome="Light", nivel=0, escola="evocacao"
        )
        svc = Dnd5eConjuracaoService(Dnd5eMagiaRepository(db))
        with pytest.raises(HTTPException) as exc:
            svc.conjurar(
                Dnd5eConjurarRequest(
                    conjurador_id="m1",
                    nome="Mago",
                    classe="mago",
                    nivel_personagem=3,
                    magia_id=magia.id,
                    mod_inteligencia=3,
                    armadura_slug="cota-anéis",
                )
            )
        assert "bloqueada" in str(exc.value.detail).lower()
    finally:
        db.close()
