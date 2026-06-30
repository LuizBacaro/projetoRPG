"""Catálogo de equipamentos — enriquecimento v1.3."""

from __future__ import annotations

from app.games.tormenta.rules.catalogo_t20 import (
    filtrar_equipamentos_mb,
    lista_equipamentos_mb_catalogo,
)


def _por_nome(nome: str) -> dict:
    for row in lista_equipamentos_mb_catalogo():
        if row.get("nome") == nome:
            return row
    raise KeyError(nome)


def test_armadura_couro_enriquecida_v13() -> None:
    row = _por_nome("Armadura de couro")
    assert row.get("tipo") == "leve"
    assert row.get("bonus_ca") == 2
    assert row.get("espacos") == 2
    assert row.get("regra_versao") == "v13"


def test_brunea_no_catalogo_equipamentos() -> None:
    row = _por_nome("Brunea")
    assert row.get("tipo") == "pesada"
    assert row.get("bonus_ca") == 5
    assert row.get("espacos") == 5


def test_mochila_zero_espacos() -> None:
    row = _por_nome("Mochila")
    assert row.get("espacos") == 0


def test_pocao_meio_espaco() -> None:
    row = _por_nome("Poção de cura (frasco)")
    assert row.get("espacos") == 0.5


def test_clava_overlay_v13() -> None:
    row = _por_nome("Clava")
    assert row.get("dano_m") == "1d6"
    assert row.get("proficiencia") == "simples"
    assert row.get("regra_versao") == "v13"


def test_espada_longa_overlay_v13() -> None:
    row = _por_nome("Espada longa")
    assert row.get("dano_m") == "1d8"
    assert row.get("proficiencia") == "marcial"
    assert row.get("critico") == "19"


def test_adaga_mantem_stats_mb() -> None:
    row = _por_nome("Adaga")
    assert row.get("dano_p") == "1d3"
    assert row.get("dano_m") == "1d4"
    assert row.get("regra_versao") == "v13"


def test_busca_equipamento_prioriza_match_exato() -> None:
    rows, total = filtrar_equipamentos_mb("Armadura de couro", 0, 1)
    assert total >= 1
    assert rows[0]["nome"] == "Armadura de couro"
