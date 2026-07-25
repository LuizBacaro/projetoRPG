"""Catálogo itens superiores / materiais especiais v1.3."""

from app.games.tormenta.rules.itens_superiores_v13_t20 import (
    custo_melhorias_ts,
    lista_materiais_especiais_v13,
    lista_melhorias_v13,
    precos_melhoria_v13,
    resumo_itens_superiores_v13,
)


def test_precos_tabela_3_7():
    assert precos_melhoria_v13() == [300, 3000, 9000, 18000]
    assert custo_melhorias_ts(1) == 300
    assert custo_melhorias_ts(2) == 3300
    assert custo_melhorias_ts(4) == 30300


def test_melhorias_filtro_arma():
    armas = lista_melhorias_v13(aplica_em="arma")
    assert any(m["slug"] == "certeira" for m in armas)
    assert all("arma" in m["aplica_em"] for m in armas)
    certeira = next(m for m in armas if m["slug"] == "certeira")
    assert certeira["mods"].get("ataque") == 1


def test_materiais_adamante():
    mats = lista_materiais_especiais_v13(aplica_em="arma")
    ada = next(m for m in mats if m["slug"] == "adamante")
    assert ada["custo_ts"]["arma"] == 3000


def test_resumo_completo():
    r = resumo_itens_superiores_v13()
    assert len(r["melhorias"]) >= 25
    assert len(r["materiais"]) == 6
