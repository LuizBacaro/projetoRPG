"""Grimório e papéis de magia — Arcanista v1.3 por caminho."""

from __future__ import annotations

from app.games.tormenta.rules.grimorio_conjuracao_t20 import (
    modo_conjuracao_classe,
    slug_efetivo_tabelas_magia_mb,
    validar_papel_magia_para_classe,
)
from app.games.tormenta.rules.grimorio_elegibilidade_t20 import (
    resumo_elegibilidade_grimorio_mb,
)
from app.games.tormenta.rules.magias_conhecidas_progressao_t20 import (
    classe_usa_limite_conhecidas_mb,
)
from app.games.tormenta.rules.magias_grimorio_aprendizado_t20 import (
    classe_usa_limite_grimorio_mb,
)
from app.games.tormenta.rules.regra_versao_t20 import REGRA_VERSAO_V13


def test_arcanista_mago_modo_preparar_e_grimorio():
    assert modo_conjuracao_classe("arcanista", REGRA_VERSAO_V13, "mago") == "preparar"
    assert (
        slug_efetivo_tabelas_magia_mb("arcanista", REGRA_VERSAO_V13, "mago") == "mago"
    )
    assert classe_usa_limite_grimorio_mb(
        "arcanista", regra_versao=REGRA_VERSAO_V13, arcanista_caminho="mago"
    )
    ok, _ = validar_papel_magia_para_classe(
        "arcanista",
        "grimorio",
        regra_versao=REGRA_VERSAO_V13,
        arcanista_caminho="mago",
    )
    assert ok is True
    ok2, msg2 = validar_papel_magia_para_classe(
        "arcanista",
        "conhecida",
        regra_versao=REGRA_VERSAO_V13,
        arcanista_caminho="mago",
    )
    assert ok2 is False
    assert "grimório" in msg2.lower()


def test_arcanista_feiticeiro_espontaneo_conhecidas():
    assert (
        modo_conjuracao_classe("arcanista", REGRA_VERSAO_V13, "feiticeiro")
        == "espontaneo"
    )
    assert not classe_usa_limite_grimorio_mb(
        "arcanista", regra_versao=REGRA_VERSAO_V13, arcanista_caminho="feiticeiro"
    )
    assert classe_usa_limite_conhecidas_mb(
        "arcanista", regra_versao=REGRA_VERSAO_V13, arcanista_caminho="feiticeiro"
    )
    ok, _ = validar_papel_magia_para_classe(
        "arcanista",
        "conhecida",
        regra_versao=REGRA_VERSAO_V13,
        arcanista_caminho="feiticeiro",
    )
    assert ok is True
    ok2, _ = validar_papel_magia_para_classe(
        "arcanista",
        "grimorio",
        regra_versao=REGRA_VERSAO_V13,
        arcanista_caminho="feiticeiro",
    )
    assert ok2 is False


def test_arcanista_bruxo_foco_apenas_conhecida():
    assert modo_conjuracao_classe("arcanista", REGRA_VERSAO_V13, "bruxo") == "foco"
    assert classe_usa_limite_conhecidas_mb(
        "arcanista", regra_versao=REGRA_VERSAO_V13, arcanista_caminho="bruxo"
    )
    ok, _ = validar_papel_magia_para_classe(
        "arcanista",
        "conhecida",
        regra_versao=REGRA_VERSAO_V13,
        arcanista_caminho="bruxo",
    )
    assert ok is True
    ok2, msg2 = validar_papel_magia_para_classe(
        "arcanista",
        "grimorio",
        regra_versao=REGRA_VERSAO_V13,
        arcanista_caminho="bruxo",
    )
    assert ok2 is False
    assert "foco" in msg2.lower()
    ok3, _ = validar_papel_magia_para_classe(
        "arcanista",
        "preparada",
        regra_versao=REGRA_VERSAO_V13,
        arcanista_caminho="bruxo",
    )
    assert ok3 is False


def test_elegibilidade_arcanista_v13_exige_caminho():
    ok, msg = resumo_elegibilidade_grimorio_mb(
        tipo="jogador",
        nivel=1,
        ficha_json={
            "regra_versao": "v13",
            "tormenta_classe_mb_slug": "arcanista",
        },
    )
    assert ok is False
    assert "caminho" in msg.lower()

    ok2, msg2 = resumo_elegibilidade_grimorio_mb(
        tipo="jogador",
        nivel=1,
        ficha_json={
            "regra_versao": "v13",
            "tormenta_classe_mb_slug": "arcanista",
            "arcanista_caminho": "mago",
        },
    )
    assert ok2 is True
    assert msg2 == ""
