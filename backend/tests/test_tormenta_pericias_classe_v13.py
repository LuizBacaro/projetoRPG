"""Perícias de classe v1.3 — fixas, «ou» e pool."""

from __future__ import annotations

from app.games.tormenta.rules.pericias_classe_t20 import (
    config_pericias_classe_v13,
    vagas_classe_v13,
    validar_pericias_classe_v13,
)
from app.games.tormenta.rules.pericias_criacao_t20 import (
    vagas_pericias_treinadas,
    validar_pericias_ficha,
)


def _per(nome: str, treinado: bool = True) -> dict:
    return {"nome": nome, "treinado": treinado}


def test_vagas_barbaro_v13_inclui_fixas() -> None:
    v = vagas_pericias_treinadas("barbaro", 2, regra_versao="v13")
    assert v == 6 + 2


def test_barbaro_v13_pericias_ok() -> None:
    per = [
        _per("Fortitude"),
        _per("Luta"),
        _per("Atletismo"),
        _per("Cavalgar"),
        _per("Iniciativa"),
        _per("Intimidação"),
    ]
    ok, _, _ = validar_pericias_ficha(
        nivel=1,
        slug_classe="barbaro",
        int_valor=2,
        slug_raca=None,
        pericias=per,
        regra_versao="v13",
    )
    assert ok is True


def test_barbaro_v13_falta_fixa() -> None:
    per = [
        _per("Luta"),
        _per("Atletismo"),
        _per("Cavalgar"),
        _per("Iniciativa"),
        _per("Intimidação"),
    ]
    ok, motivo, _ = validar_pericias_ficha(
        nivel=1,
        slug_classe="barbaro",
        int_valor=0,
        slug_raca=None,
        pericias=per,
        regra_versao="v13",
    )
    assert ok is False
    assert "fortitude" in motivo.lower()


def test_bucaneiro_v13_luta_ou_pontaria() -> None:
    cfg = config_pericias_classe_v13("bucaneiro")
    assert cfg is not None
    assert cfg["pericias_escolha_um_de"] == [["luta", "pontaria"]]
    per = [
        _per("Reflexos"),
        _per("Luta"),
        _per("Acrobacia"),
        _per("Atletismo"),
        _per("Enganação"),
        _per("Iniciativa"),
    ]
    ok, _, _ = validar_pericias_classe_v13(
        slug_classe="bucaneiro",
        pericias=per,
        int_valor=0,
        slug_raca=None,
        int_extra=0,
        racial_extra=0,
    )
    assert ok is True


def test_arcanista_v13_pool() -> None:
    cfg = config_pericias_classe_v13("arcanista")
    assert cfg is not None
    assert "misticismo" in cfg["pericias_fixas"]
    assert cfg["pericias_escolha_qtd"] == 2
    assert "conhecimento" in cfg["pericias_escolha_de"]
    assert vagas_classe_v13("arcanista") == 4
