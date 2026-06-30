"""Classes Tormenta 20 v1.3 — lista, PV e PM por classe."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.classes_t20 import (
    lista_classes,
    lista_classes_mb,
    lista_classes_v13,
)
from app.games.tormenta.rules.progressao_pv_t20 import pv_maximos_mb


def test_lista_classes_v13_quatorze() -> None:
    rows = lista_classes_v13()
    assert len(rows) == 14
    slugs = {r["slug"] for r in rows}
    assert "arcanista" in slugs
    assert "cacador" in slugs
    assert "bucaneiro" in slugs
    assert "mago" not in slugs
    assert "feiticeiro" not in slugs
    assert "ranger" not in slugs


def test_lista_classes_mb_legado() -> None:
    rows = lista_classes_mb()
    assert len(rows) >= 13
    slugs = {r["slug"] for r in rows}
    assert "mago" in slugs or "barbaro" in slugs


def test_lista_classes_regra_versao() -> None:
    v13 = lista_classes("v13")
    mb = lista_classes("mb")
    assert len(v13) == 14
    assert len(mb) != len(v13)


def test_pm_por_nivel_v13() -> None:
    arc = next(r for r in lista_classes_v13() if r["slug"] == "arcanista")
    bar = next(r for r in lista_classes_v13() if r["slug"] == "barbaro")
    cac = next(r for r in lista_classes_v13() if r["slug"] == "cacador")
    assert arc.get("pm_por_nivel") == 6
    assert bar.get("pm_por_nivel") == 3
    assert cac.get("pm_por_nivel") == 4


def test_pv_barbaro_v13_con_2() -> None:
    """Bárbaro 1º nível, CON 2 → PV 26 (24 + 2)."""
    pv = pv_maximos_mb("barbaro", 1, 2, regra_versao="v13")
    assert pv == 26


def test_pm_barbaro_v13_nivel_1() -> None:
    from app.games.tormenta.rules.progressao_pv_t20 import preview_pv_mb

    prev = preview_pv_mb("barbaro", 1, 2, regra_versao="v13")
    assert prev["pv_max"] == 26
    assert prev["pm_por_nivel"] == 3
    assert prev["pm_max"] == 3


def test_pm_arcanista_v13_nivel_1() -> None:
    from app.games.tormenta.rules.progressao_pv_t20 import preview_pv_mb

    prev = preview_pv_mb("arcanista", 1, 0, regra_versao="v13")
    assert prev["pv_max"] == 8
    assert prev["pm_por_nivel"] == 6
    assert prev["pm_max"] == 6


def test_pv_arcanista_v13_con_0() -> None:
    pv = pv_maximos_mb("arcanista", 1, 0, regra_versao="v13")
    assert pv == 8
