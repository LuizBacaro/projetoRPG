"""Testes HA-1 — mecânicas raciais Heróis de Arton."""

from __future__ import annotations

from app.games.tormenta.rules.combate_t20 import (
    ataque_bonus_tamanho_combate,
    ca_bonus_tamanho_combate,
    expandir_dano_forca_dos_titas,
    manobra_bonus_tamanho,
    rolar_teste_vontade_racial,
)
from app.games.tormenta.rules.conjuracao_t20 import (
    habilidade_chave_conjuracao_efetiva,
    instrumentista_magico_racial,
    pm_aprimoramento_bonus_racial,
    pode_conjurar_via_instrumento,
)
from app.games.tormenta.rules.poderes_ficha_v13_t20 import listar_poderes_sync_v13
from app.games.tormenta.rules.poderes_herois_arton_t20 import raca_atende_exigencia
from app.games.tormenta.rules.progressao_pv_t20 import pm_bonus_racial_ha_de_ficha
from app.games.tormenta.rules.tracos_raciais_t20 import preview_tracos_raciais


def test_preview_galokk_tamanho_grande() -> None:
    p = preview_tracos_raciais("galokk", regra_versao="v13")
    assert p["encontrado"] is True
    assert p["tamanho"] == "grande"
    assert p["tamanho_label"] == "Grande"
    assert p["ca_bonus"] == -1
    assert p["ataque_bonus"] == 1
    assert p["manobra_bonus"] == 2
    assert p["armas_aumentadas"] is True
    assert p["furtividade_bonus"] == -4
    assert any("Força dos Titãs" in x for x in p["escolhas_resumo"])


def test_modificadores_tamanho_grande_vs_medio() -> None:
    assert ca_bonus_tamanho_combate("grande", "medio") == -1
    assert ataque_bonus_tamanho_combate("grande", "medio") == 1
    assert manobra_bonus_tamanho("grande") == 2


def test_forca_dos_titas_dado_extra_com_limite() -> None:
    rolls, soma = expandir_dano_forca_dos_titas([8], 8, 2, seed=1)
    assert len(rolls) >= 2
    assert soma == sum(rolls)


def test_eiradaan_cancao_melancolia_pior_d20() -> None:
    r = rolar_teste_vontade_racial(
        3, 15, slug_raca="eiradaan", efeito_mental=True, seed=42
    )
    assert r["cancao_melancolia"] is True
    assert len(r["d20_rolagens"]) == 2
    assert r["d20"] == min(r["d20_rolagens"])


def test_eiradaan_magia_instintiva_sab() -> None:
    assert (
        habilidade_chave_conjuracao_efetiva("arcanista", "v13", None, "eiradaan")
        == "sab"
    )
    assert pm_aprimoramento_bonus_racial("eiradaan") == 1


def test_satiro_instrumentista_magico() -> None:
    p = preview_tracos_raciais("satiro", regra_versao="v13")
    assert p["fortitude_bonus"] == 2
    assert p["pericias_bonus"].get("Atuação") == 2
    assert instrumentista_magico_racial("satiro") is True
    assert pode_conjurar_via_instrumento("satiro", instrumento_empunhado=True) is True
    assert pode_conjurar_via_instrumento("satiro", instrumento_empunhado=False) is False


def test_meio_elfo_pm_impar_e_ambicao_sync() -> None:
    assert (
        pm_bonus_racial_ha_de_ficha(
            {"game_suplemento": "herois_arton", "raca_tormenta_slug": "meio_elfo"},
            3,
        )
        == 2
    )
    assert raca_atende_exigencia("elfo", "meio_elfo") is True
    p = preview_tracos_raciais("meio_elfo", regra_versao="v13")
    assert any("Ambição Herdada" in x for x in p["escolhas_resumo"])
    sync = listar_poderes_sync_v13(
        {
            "regra_versao": "v13",
            "raca_tormenta_slug": "meio_elfo",
            "ambicao_herdada_poder_slug": "ataque_poderoso",
        }
    )
    assert any(x["slug"] == "ataque_poderoso" for x in sync)


def test_preview_eiradaan_tracos_resumo() -> None:
    p = preview_tracos_raciais("eiradaan", regra_versao="v13")
    resumo = " ".join(p["escolhas_resumo"])
    assert "Sentidos Místicos" in resumo
    assert "Canção da Melancolia" in resumo
