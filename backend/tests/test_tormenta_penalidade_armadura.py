"""Penalidade de armadura em perícias — Tormenta 20 v1.3."""

from __future__ import annotations

from app.games.tormenta.rules.atributos_t20 import lista_pericias_com_atributo
from app.games.tormenta.rules.penalidade_armadura_t20 import (
    penalidade_armadura_pericia,
    penalidade_equipada_total,
    pericia_aplica_penalidade_armadura,
)


def _meta(slug: str) -> dict:
    for row in lista_pericias_com_atributo("v13"):
        if row.get("slug") == slug:
            return row
    raise KeyError(slug)


def test_penalidade_equipada_armadura_escudo() -> None:
    itens = [
        {"nome": "Cota de malha", "tipo": "media", "penalidade": -2},
        {"nome": "Escudo leve", "tipo": "escudo", "penalidade": -1},
    ]
    assert penalidade_equipada_total(itens) == 3


def test_acrobacia_com_armadura_pesada() -> None:
    meta = _meta("acrobacia")
    itens = [{"nome": "Peitoral", "tipo": "pesada", "penalidade": -4}]
    assert penalidade_armadura_pericia(meta, itens) == 4


def test_diplomacia_sem_penalidade() -> None:
    meta = _meta("diplomacia")
    itens = [{"nome": "Peitoral", "tipo": "pesada", "penalidade": -4}]
    assert penalidade_armadura_pericia(meta, itens) == 0


def test_atletismo_escalada_sem_penalidade() -> None:
    meta = _meta("atletismo")
    itens = [{"nome": "Placas", "tipo": "pesada", "penalidade": -5}]
    assert penalidade_armadura_pericia(meta, itens, uso_atletismo_natacao=False) == 0


def test_atletismo_natacao_com_penalidade() -> None:
    meta = _meta("atletismo")
    itens = [
        {"nome": "Placas", "tipo": "pesada", "penalidade": -5},
        {"nome": "Escudo pesado", "tipo": "escudo", "penalidade": -2},
    ]
    assert penalidade_armadura_pericia(meta, itens, uso_atletismo_natacao=True) == 7


def test_pericia_aplica_flag_natacao() -> None:
    meta = _meta("atletismo")
    assert (
        pericia_aplica_penalidade_armadura(meta, uso_atletismo_natacao=False) is False
    )
    assert pericia_aplica_penalidade_armadura(meta, uso_atletismo_natacao=True) is True


def test_furtividade_ladinagem_acumulam() -> None:
    meta = _meta("furtividade")
    itens = [
        {"nome": "Couro reforçado", "tipo": "leve", "penalidade": -1},
        {"nome": "Broquel", "tipo": "escudo", "penalidade": 0},
    ]
    assert penalidade_armadura_pericia(meta, itens) == 1
