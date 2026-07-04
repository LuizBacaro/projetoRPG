"""Testes Duende — Heróis de Arton HA-1."""

from __future__ import annotations

from app.games.tormenta.rules.duende_t20 import (
    calcular_modificadores_atributos_duende,
    lista_presentes_duende,
    opcoes_duende_catalogo,
    validar_duende_ficha,
)
from app.games.tormenta.rules.racas_t20 import lista_racas_herois_arton


def _ficha_duende_minima(**overrides):
    base = {
        "regra_versao": "v13",
        "raca_tormenta_slug": "duende",
        "duende": {
            "natureza": "animal",
            "natureza_atributo": "des",
            "tamanho_raca": "medio",
            "dons": ["car", "int"],
            "presentes": ["invisibilidade", "voo", "lingua_da_natureza"],
            "tabu_texto": "Nunca senta em cadeiras",
            "tabu_penalidade": "diplomacia",
            "geracao_aleatoria": False,
            "presentes_opcoes": {},
        },
    }
    if overrides:
        du = dict(base["duende"])
        du.update(overrides.get("duende") or {})
        base["duende"] = du
        for k, v in overrides.items():
            if k != "duende":
                base[k] = v
    return base


def test_duende_no_catalogo_ha() -> None:
    rows = lista_racas_herois_arton()
    slugs = {r["slug"] for r in rows}
    assert "duende" in slugs
    du = next(r for r in rows if r["slug"] == "duende")
    assert du.get("construcao_modular_duende") is True


def test_lista_presentes_duende_doze() -> None:
    rows = lista_presentes_duende()
    assert len(rows) == 12
    slugs = {r["slug"] for r in rows}
    assert "voo" in slugs
    assert "maldicao" in slugs


def test_validar_duende_ok() -> None:
    ok, msg = validar_duende_ficha(_ficha_duende_minima())
    assert ok, msg


def test_validar_duende_faltando_presentes() -> None:
    f = _ficha_duende_minima(duende={"presentes": ["voo", "invisibilidade"]})
    ok, msg = validar_duende_ficha(f)
    assert not ok
    assert "Presentes" in msg


def test_validar_duende_maldicao_exige_opcoes() -> None:
    f = _ficha_duende_minima(
        duende={
            "presentes": ["maldicao", "voo", "invisibilidade"],
            "presentes_opcoes": {},
        }
    )
    ok, msg = validar_duende_ficha(f)
    assert not ok
    assert "Maldição" in msg


def test_calcular_modificadores_duende_animal_medio() -> None:
    cfg = _ficha_duende_minima()["duende"]
    mods = calcular_modificadores_atributos_duende(cfg)
    assert mods["des"] == 1
    assert mods["car"] == 1
    assert mods["int"] == 1


def test_opcoes_duende_catalogo() -> None:
    op = opcoes_duende_catalogo()
    assert len(op["naturezas"]) == 3
    assert len(op["tamanhos"]) == 4
    assert op["qtd_presentes"] == 3
