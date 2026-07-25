"""Traços raciais na ficha — Defesa, PV/PM e armas naturais (v1.3)."""

from __future__ import annotations

from app.games.tormenta.rules.defesa_t20 import ca_efetiva_personagem, defesa_total_v13
from app.games.tormenta.rules.progressao_pv_t20 import preview_pv_mb
from app.games.tormenta.rules.tracos_raciais_t20 import (
    _carregar_tracos,
    ca_bonus_racial,
    contrib_pm_racial,
    contrib_pv_racial,
    preview_tracos_raciais,
)


def setup_module() -> None:
    _carregar_tracos.cache_clear()


def test_minotauro_ca_bonus_couro_rigido() -> None:
    assert ca_bonus_racial("minotauro", "v13") == 1
    prev = preview_tracos_raciais("minotauro", regra_versao="v13")
    assert prev["ca_bonus"] == 1
    assert prev["ca_bonus_label"] == "Couro Rígido"
    assert prev["arma_natural"]["nome"] == "Chifres"
    assert prev["arma_natural"]["dano"] == "1d6"


def test_minotauro_defesa_total_inclui_racial() -> None:
    assert defesa_total_v13(0, [], outros_bonus=1) == 11
    fj = {"regra_versao": "v13", "raca_tormenta_slug": "minotauro"}
    assert ca_efetiva_personagem(des_valor=0, ca=10, ficha_json=fj) == 11


def test_minotauro_sem_sobrevivencia_fixa_v13() -> None:
    prev = preview_tracos_raciais("minotauro", regra_versao="v13")
    assert prev.get("pericias_bonus") == {}


def test_anao_pv_racial() -> None:
    assert contrib_pv_racial("anao", 1, "v13") == 3
    assert contrib_pv_racial("anao", 3, "v13") == 5
    prev = preview_pv_mb("clerigo", 1, 4, regra_versao="v13", slug_raca="anao")
    # 16 + 0 níveis + 4 CON + 3 Anão
    assert prev["pv_max"] == 23
    assert prev["contrib_pv_racial"] == 3


def test_elfo_pm_racial() -> None:
    assert contrib_pm_racial("elfo", 2, "v13") == 2
    prev = preview_pv_mb("arcanista", 1, 0, regra_versao="v13", slug_raca="elfo")
    assert prev["contrib_pm_racial"] == 1
    assert prev["pm_max"] is not None
    assert prev["pm_max"] >= 1


def test_trog_arma_natural_e_ca() -> None:
    prev = preview_tracos_raciais("trog", regra_versao="v13")
    assert prev["ca_bonus"] == 1
    assert prev["arma_natural"]["nome"] == "Mordida"
    assert prev["furtividade_sem_armadura"] == 5
    assert prev["furtividade_bonus"] == 0


def test_kliren_medio_sem_ca_tamanho() -> None:
    prev = preview_tracos_raciais("kliren", regra_versao="v13")
    assert prev["tamanho"] == "medio"
    assert prev["deslocamento_m"] == 9
    assert prev["ca_bonus"] == 0
