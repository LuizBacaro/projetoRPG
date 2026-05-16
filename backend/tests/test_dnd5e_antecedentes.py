"""Regras D&D 5E — antecedentes."""

import random

from app.games.dnd5e.rules.antecedentes import (
    PersonagemAntecedente,
    antecedente_do_catalogo,
    aplicar_antecedente,
    gerar_tracos,
    listar_antecedentes,
)


def test_treze_antecedentes() -> None:
    assert len(listar_antecedentes()) == 13


def test_aplica_pericias_idiomas_ouro() -> None:
    ant = antecedente_do_catalogo("acolito")
    assert ant is not None
    p = PersonagemAntecedente(pericias=["Athletics"])
    aplicar_antecedente(p, ant)
    assert "Insight" in p.pericias
    assert "Religion" in p.pericias
    assert len(p.idiomas) == 1
    assert p.ouro == 15
    assert len(p.pericias) == 3


def test_sem_duplicata_pericia() -> None:
    ant = antecedente_do_catalogo("acolito")
    assert ant is not None
    p = PersonagemAntecedente(pericias=["Insight"])
    aplicar_antecedente(p, ant)
    assert p.pericias.count("Insight") == 1


def test_gerar_tracos_duas_por_categoria() -> None:
    ant = antecedente_do_catalogo("soldado")
    assert ant is not None
    tr = gerar_tracos(ant, rng=random.Random(42))
    assert len(tr.personalidade) == 2
    assert len(tr.ideais) == 2
    assert len(tr.lacos) == 2
    assert len(tr.fraquezas) == 2
