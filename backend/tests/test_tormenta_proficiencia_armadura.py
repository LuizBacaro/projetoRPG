"""Proficiência de armadura — Tormenta 20 v1.3 (RF-T07e-1)."""

from __future__ import annotations

from app.games.tormenta.rules.atributos_t20 import lista_pericias_com_atributo
from app.games.tormenta.rules.penalidade_armadura_t20 import (
    penalidade_armadura_pericia,
    pericia_aplica_penalidade_armadura,
)
from app.games.tormenta.rules.proficiencia_armadura_t20 import (
    proficiencias_armadura_classe,
    proficiente_em_protecao,
    tem_protecao_sem_proficiencia,
)


def _meta(slug: str) -> dict:
    for row in lista_pericias_com_atributo("v13"):
        if row.get("slug") == slug:
            return row
    raise KeyError(slug)


def test_arcanista_sem_proficiencia_armadura() -> None:
    prof = proficiencias_armadura_classe("arcanista")
    assert prof["leve"] is False
    item = {"nome": "Couro", "tipo": "leve", "penalidade": -1, "bonus_ca": 2}
    assert proficiente_em_protecao(prof, item) is False


def test_guerreiro_proficiente_pesada() -> None:
    prof = proficiencias_armadura_classe("guerreiro")
    item = {"nome": "Placas", "tipo": "pesada", "penalidade": -5, "bonus_ca": 10}
    assert proficiente_em_protecao(prof, item) is True
    assert tem_protecao_sem_proficiencia([item], "guerreiro") is False


def test_luta_arcanista_com_armadura_pesada_penalidade() -> None:
    meta = _meta("luta")
    itens = [{"nome": "Placas", "tipo": "pesada", "penalidade": -5}]
    assert penalidade_armadura_pericia(meta, itens, slug_classe="guerreiro") == 0
    assert penalidade_armadura_pericia(meta, itens, slug_classe="arcanista") == 5


def test_pontaria_nao_proficiente_com_escudo() -> None:
    meta = _meta("pontaria")
    itens = [{"nome": "Escudo leve", "tipo": "escudo", "penalidade": -1, "bonus_ca": 1}]
    assert penalidade_armadura_pericia(meta, itens, slug_classe="guerreiro") == 0
    assert penalidade_armadura_pericia(meta, itens, slug_classe="arcanista") == 1


def test_atletismo_nao_proficiente_sem_natacao() -> None:
    meta = _meta("atletismo")
    itens = [{"nome": "Couro", "tipo": "leve", "penalidade": -1}]
    assert (
        penalidade_armadura_pericia(
            meta, itens, uso_atletismo_natacao=False, slug_classe="arcanista"
        )
        == 1
    )


def test_pericia_aplica_nao_proficiente_for_des() -> None:
    meta = _meta("iniciativa")
    assert (
        pericia_aplica_penalidade_armadura(meta, nao_proficiente_armadura=True) is True
    )
    meta_int = _meta("conhecimento")
    assert (
        pericia_aplica_penalidade_armadura(meta_int, nao_proficiente_armadura=True)
        is False
    )
