"""Regras D&D 5E — antecedentes."""

import random

from app.games.dnd5e.rules.antecedentes import (
    PersonagemAntecedente,
    antecedente_do_catalogo,
    aplicar_antecedente,
    gerar_tracos,
    listar_antecedentes,
    sincronizar_antecedente_na_ficha,
)


def test_treze_antecedentes() -> None:
    assert len(listar_antecedentes()) == 13


def test_aplica_pericias_idiomas_ouro() -> None:
    ant = antecedente_do_catalogo("acolito")
    assert ant is not None
    p = PersonagemAntecedente(pericias=["Athletics"])
    aplicar_antecedente(p, ant, idiomas_escolhidos=["elfico"])
    assert "Insight" in p.pericias
    assert "Religion" in p.pericias
    assert p.idiomas == ["elfico"]
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
    assert len(tr.personalidade) == 1
    assert len(tr.ideais) == 1
    assert len(tr.lacos) == 1
    assert len(tr.fraquezas) == 1


def test_sincronizar_inventario_antecedente() -> None:
    ficha = {
        "antecedente_slug": "acolito",
        "inventario": {"equipamentos": [], "ouro_po": 5},
    }
    out = sincronizar_antecedente_na_ficha(ficha, rng=random.Random(1))
    inv = out["inventario"]
    assert out["antecedente_inventario_slug"] == "acolito"
    assert out["antecedente_ouro_aplicado"] == 15
    assert inv["ouro_po"] == 20
    assert len(inv["equipamentos"]) == 3
    assert all(item["fonte"] == "antecedente" for item in inv["equipamentos"])
    assert len(out["antecedente_tracos"]["personalidade"]) == 0
    assert out["antecedente_idiomas"] == []


def test_sincronizar_troca_antecedente_remove_anterior() -> None:
    ficha = sincronizar_antecedente_na_ficha(
        {
            "antecedente_slug": "acolito",
            "inventario": {"equipamentos": [], "ouro_po": 0},
        },
        rng=random.Random(1),
    )
    ficha["antecedente_slug"] = "nobre"
    out = sincronizar_antecedente_na_ficha(ficha, rng=random.Random(2))
    inv = out["inventario"]
    assert out["antecedente_inventario_slug"] == "nobre"
    assert out["antecedente_ouro_aplicado"] == 25
    assert inv["ouro_po"] == 25
    assert len(inv["equipamentos"]) == 2
    assert all(item["antecedente_slug"] == "nobre" for item in inv["equipamentos"])
