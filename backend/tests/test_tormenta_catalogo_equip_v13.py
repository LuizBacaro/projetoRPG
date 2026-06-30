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
    assert row.get("empunhadura") == "uma mão"
    assert row.get("espacos") == 1
    assert row.get("regra_versao") == "v13"


def test_espada_longa_overlay_v13() -> None:
    row = _por_nome("Espada longa")
    assert row.get("dano_m") == "1d8"
    assert row.get("proficiencia") == "marcial"
    assert row.get("critico") == "19"


def test_cimitarra_overlay_v13() -> None:
    row = _por_nome("Cimitarra")
    assert row.get("dano_m") == "1d6"
    assert row.get("proficiencia") == "marcial"
    assert row.get("critico") == "18"


def test_katana_wakizashi_overlay_lote2() -> None:
    kat = _por_nome("Espada samurai (katana)")
    assert kat.get("dano_m") == "1d8/1d10"
    assert kat.get("proficiencia") == "exotica"
    assert kat.get("critico") == "19"
    assert kat.get("regra_versao") == "v13"
    wak = _por_nome("Wakizashi")
    assert wak.get("dano_m") == "1d6"
    assert wak.get("critico") == "19"
    assert wak.get("regra_versao") == "v13"


def test_machado_guerra_overlay_lote3() -> None:
    from app.games.tormenta.rules.catalogo_armas_v13_t20 import mapa_armas_v13_por_nome

    row = mapa_armas_v13_por_nome().get("machado de guerra")
    assert row is not None
    assert row.get("dano_m") == "1d12"
    assert row.get("critico") == "×3"


def test_besta_pesada_overlay_lote3() -> None:
    from app.games.tormenta.rules.catalogo_armas_v13_t20 import mapa_armas_v13_por_nome

    row = mapa_armas_v13_por_nome().get("besta pesada")
    assert row is not None
    assert row.get("dano_m") == "1d12"


def test_tacape_picareta_overlay_lote4() -> None:
    from app.games.tormenta.rules.catalogo_armas_v13_t20 import mapa_armas_v13_por_nome

    tac = mapa_armas_v13_por_nome().get("tacape")
    assert tac is not None
    assert tac.get("dano_m") == "1d10"
    assert tac.get("proficiencia") == "simples"
    pic = _por_nome("Picareta")
    assert pic.get("dano_m") == "1d6"
    assert pic.get("critico") == "×4"
    assert pic.get("proficiencia") == "marcial"
    assert pic.get("regra_versao") == "v13"


def test_municoes_overlay_lote4() -> None:
    flechas = _por_nome("Flechas (20)")
    assert flechas.get("custo") == "T$ 1"
    assert flechas.get("peso") == "1,5 kg"
    virotes = _por_nome("Virotes (10)")
    assert virotes.get("custo") == "T$ 2"


def test_escudo_ataque_overlay_lote4() -> None:
    leve = _por_nome("Escudo leve de madeira")
    assert leve.get("dano_m") == "1d4"
    assert leve.get("bonus_ca") == 1
    pesado = _por_nome("Escudo pesado de aço")
    assert pesado.get("dano_m") == "1d6"
    assert pesado.get("bonus_ca") == 2


def test_espada_bastarda_exotica_lote4() -> None:
    row = _por_nome("Espada bastarda")
    assert row.get("proficiencia") == "exotica"
    assert row.get("dano_m") == "1d10/1d12"


def test_mangual_pesado_alias_overlay_lote4() -> None:
    from app.games.tormenta.rules.catalogo_armas_v13_t20 import mapa_armas_v13_por_nome

    row = mapa_armas_v13_por_nome().get("mangual pesado")
    assert row is not None
    assert row.get("dano_m") == "1d8"
    canon = mapa_armas_v13_por_nome().get("mangual")
    assert canon is not None
    assert row.get("dano_m") == canon.get("dano_m")


def test_tacape_mb_catalogo_overlay() -> None:
    row = _por_nome("Tacape")
    assert row.get("dano_m") == "1d10"
    assert row.get("proficiencia") == "simples"
    assert row.get("regra_versao") == "v13"


def test_adaga_mantem_stats_mb() -> None:
    row = _por_nome("Adaga")
    assert row.get("dano_p") == "1d3"
    assert row.get("dano_m") == "1d4"
    assert row.get("regra_versao") == "v13"


def test_busca_equipamento_prioriza_match_exato() -> None:
    rows, total = filtrar_equipamentos_mb("Armadura de couro", 0, 1)
    assert total >= 1
    assert rows[0]["nome"] == "Armadura de couro"
