"""Testes — concentração por dano e resistência à magia no combate MB."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.conjuracao_combate_t20 import (
    aplicar_concentracao_ao_lancar,
    aplicar_resistencia_magia_ao_lancar,
    bonus_resistencia_magia_efetivo_mb,
    cd_concentracao_por_dano_mb,
    cd_teste_resistencia_magia_mb,
    inferir_tipo_resistencia_mb,
    processar_concentracao_apos_dano_mb,
    resistencia_magia_bonus_mb,
    rolar_teste_concentracao_por_dano_mb,
    rolar_teste_resistencia_magia_mb,
)


def test_cd_resistencia_magia_mb():
    assert cd_teste_resistencia_magia_mb(3, 4) == 17


def test_cd_concentracao_por_dano():
    assert cd_concentracao_por_dano_mb(12) == 22
    assert cd_concentracao_por_dano_mb(0) == 10


def test_resistencia_magia_bonus_catalogo_mb():
    vinculos = [{"magia_slug": "resistencia_a_magia", "papel": "preparada"}]
    assert resistencia_magia_bonus_mb(vinculos) == 4
    vinculos_maior = [
        {"magia_slug": "resistencia_a_magia_maior_div", "papel": "conhecida"}
    ]
    assert resistencia_magia_bonus_mb(vinculos_maior) == 8


def test_resistencia_magia_sessao_prioriza_sobre_grimorio():
    fj = aplicar_resistencia_magia_ao_lancar({}, magia_slug="resistencia_a_magia")
    assert bonus_resistencia_magia_efetivo_mb(fj) == 4
    vinculos = [{"magia_slug": "resistencia_a_magia_maior", "papel": "preparada"}]
    assert bonus_resistencia_magia_efetivo_mb(fj, vinculos) == 4


def test_inferir_tipo_resistencia():
    assert inferir_tipo_resistencia_mb("Reflexos metade") == "reflexos"
    assert inferir_tipo_resistencia_mb("Vontade anula") == "vontade"
    assert inferir_tipo_resistencia_mb("Fortitude parcial") == "fortitude"
    assert inferir_tipo_resistencia_mb("nenhum") is None


def test_rolar_teste_resistencia_com_bonus_rm():
    r = rolar_teste_resistencia_magia_mb(
        tipo="vontade",
        von_total=5,
        bonus_rm=4,
        cd=15,
        seed=42,
    )
    assert r["bonus_base"] == 5
    assert r["bonus_resistencia_magia"] == 4
    assert r["bonus_total"] == 9
    assert r["total"] == r["d20"] + r["bonus_total"]
    assert r["passou"] == (r["total"] >= 15)


def test_concentracao_perdida_com_dano_alto_seed_fixo():
    fj = aplicar_concentracao_ao_lancar(
        {},
        magia_slug="detectar_magia",
        meta={"nome": "Detectar Magia", "duracao": "concentração"},
    )
    out = processar_concentracao_apos_dano_mb(
        fj,
        dano=25,
        con_valor=10,
        nivel=1,
        fort_total=0,
        seed=1,
    )
    assert out["tinha_concentracao"] is True
    assert out["concentracao_perdida"] is True
    assert out["teste"]["dc"] == 35
    assert out["teste"]["manteve"] is False
    assert not (out["ficha_json"].get("tormenta_grimorio_sessao_mb") or {}).get(
        "concentracao_magia_slug"
    )


def test_concentracao_mantida_com_bonus_alto():
    teste = rolar_teste_concentracao_por_dano_mb(
        dano=5,
        con_valor=18,
        nivel=10,
        fort_total=12,
        seed=20,
    )
    assert teste["dc"] == 15
    assert teste["bonus"] == 12
    assert teste["manteve"] is True


@pytest.mark.parametrize("dano,fort,seed,perde", [(3, 0, 1, True), (1, 15, 20, False)])
def test_processar_concentracao_varios_cenarios(dano, fort, seed, perde):
    fj = aplicar_concentracao_ao_lancar(
        {},
        magia_slug="x",
        meta={"duracao": "concentração"},
    )
    out = processar_concentracao_apos_dano_mb(
        fj,
        dano=dano,
        con_valor=10,
        nivel=3,
        fort_total=fort,
        seed=seed,
    )
    assert out["concentracao_perdida"] is perde
