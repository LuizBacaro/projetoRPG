"""Testes RF-T01-ui-n — migração score→nativo v1.3."""

from app.games.tormenta.rules.atributos_migracao_v13_t20 import (
    aplicar_plano_migracao,
    campo_parece_score_persistido,
    planejar_migracao_personagem,
    score_exibicao_para_nativo,
    tem_sinal_score_era,
)


def test_score_exibicao_para_nativo_tabela():
    assert score_exibicao_para_nativo(10) == 0
    assert score_exibicao_para_nativo(12) == 1
    assert score_exibicao_para_nativo(14) == 2
    assert score_exibicao_para_nativo(18) == 4
    assert score_exibicao_para_nativo(6) == -2


def test_bugbear_for_5_nao_migra():
    cols = {
        "for_valor": 5,
        "des_valor": 3,
        "con_valor": 2,
        "int_valor": -1,
        "sab_valor": 0,
        "car_valor": -2,
    }
    plano = planejar_migracao_personagem(
        personagem_id=1,
        nome="Bugbear",
        tipo="monstro",
        ficha_json={"regra_versao": "v13"},
        atributos_colunas=cols,
    )
    assert plano is None


def test_score_14_migra_para_2():
    cols = {
        "for_valor": 14,
        "des_valor": 12,
        "con_valor": 10,
        "int_valor": 10,
        "sab_valor": 10,
        "car_valor": 8,
    }
    plano = planejar_migracao_personagem(
        personagem_id=2,
        nome="Guerreiro",
        tipo="jogador",
        ficha_json={"regra_versao": "v13", "atributos_compra": {"for": 14, "des": 10}},
        atributos_colunas=cols,
    )
    assert plano is not None
    assert plano.precisa_migrar
    by_campo = {a.campo: a for a in plano.alteracoes_colunas}
    assert by_campo["for"].depois == 2
    assert by_campo["des"].depois == 1
    compra = {a.campo: a for a in plano.alteracoes_compra}
    assert compra["atributos_compra.for"].depois == 2


def test_mb_nao_migra():
    cols = {
        "for_valor": 14,
        "des_valor": 12,
        "con_valor": 10,
        "int_valor": 10,
        "sab_valor": 10,
        "car_valor": 10,
    }
    plano = planejar_migracao_personagem(
        personagem_id=3,
        nome="MB legado",
        tipo="jogador",
        ficha_json={"regra_versao": "mb"},
        atributos_colunas=cols,
    )
    assert plano is None


def test_todos_10_sem_sinal_nao_migra():
    cols = dict.fromkeys(
        ["for_valor", "des_valor", "con_valor", "int_valor", "sab_valor", "car_valor"],
        10,
    )
    assert not tem_sinal_score_era({"for": 10, "des": 10})
    assert not campo_parece_score_persistido(10, sinal_score_era=False)
    plano = planejar_migracao_personagem(
        personagem_id=4,
        nome="Ambíguo",
        tipo="jogador",
        ficha_json={"regra_versao": "v13"},
        atributos_colunas=cols,
    )
    assert plano is None


def test_aplicar_plano_grava_auditoria():
    cols = {
        "for_valor": 16,
        "des_valor": 10,
        "con_valor": 10,
        "int_valor": 10,
        "sab_valor": 10,
        "car_valor": 10,
    }
    plano = planejar_migracao_personagem(
        personagem_id=5,
        nome="Arcanista",
        tipo="jogador",
        ficha_json={"regra_versao": "v13"},
        atributos_colunas=cols,
    )
    assert plano is not None
    row = {**cols, "ficha_json": {"regra_versao": "v13"}}
    aplicar_plano_migracao(row, plano)
    assert row["for_valor"] == 3
    assert row["des_valor"] == 0
    audit = row["ficha_json"]["_migracao_atributos_v13_score"]
    assert audit["colunas_antes"]["for_valor"] == 16
    assert audit["colunas_depois"]["for_valor"] == 3
