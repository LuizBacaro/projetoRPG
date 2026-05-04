"""Ordem de turno GURPS: VB, DX, sorteio (G0.1)."""

from __future__ import annotations

import random
from decimal import Decimal

from app.games.gurps.core.ordem_combate import ordenar_personagens_para_turno_gurps
from app.games.gurps.models.personagem import GurpsPersonagem


def _p(nome: str, vb: str | float, dx: int) -> GurpsPersonagem:
    return GurpsPersonagem(
        nome=nome,
        tipo="jogador",
        velocidade_valor=Decimal(str(vb)),
        dx_valor=dx,
    )


def test_ordena_por_velocidade_basica_decrescente():
    lento = _p("L", "4.00", 14)
    rapido = _p("R", "6.25", 10)
    out = ordenar_personagens_para_turno_gurps([lento, rapido], rng=random.Random(1))
    assert [x.nome for x in out] == ["R", "L"]


def test_empate_vb_usa_dx_decrescente():
    a = _p("A", "5.00", 10)
    b = _p("B", "5.00", 12)
    out = ordenar_personagens_para_turno_gurps([a, b], rng=random.Random(1))
    assert [x.nome for x in out] == ["B", "A"]


def test_empate_vb_e_dx_mesma_semente_repete_ordem():
    a = _p("A", "5.00", 10)
    b = _p("B", "5.00", 10)
    o1 = ordenar_personagens_para_turno_gurps([a, b], rng=random.Random(12345))
    o2 = ordenar_personagens_para_turno_gurps([a, b], rng=random.Random(12345))
    assert [p.nome for p in o1] == [p.nome for p in o2]
