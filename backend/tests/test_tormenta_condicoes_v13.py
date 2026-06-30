"""Condições Tormenta 20 v1.3 — catálogo p.394 e motor de combate."""

from __future__ import annotations

from app.games.tormenta.rules.catalogo_armas_v13_t20 import lista_armas_v13_overlay
from app.games.tormenta.rules.combate_t20 import modificadores_de_condicoes_mb
from app.games.tormenta.rules.condicoes_t20 import (
    lista_condicoes_v13,
    modificadores_de_condicoes,
    resolver_entrada_condicao,
)


def test_lista_condicoes_v13_fechada() -> None:
    rows = lista_condicoes_v13()
    assert len(rows) >= 30
    slugs = {r["slug"] for r in rows}
    assert "desprevenido" in slugs
    assert "vulneravel" in slugs
    assert "enredado" in slugs


def test_modificadores_desprevenido_v13() -> None:
    m = modificadores_de_condicoes(["Desprevenido"])
    assert m["ataque"] == 0
    assert m["ca"] == -5


def test_modificadores_agarrado_implica_desprevenido() -> None:
    m = modificadores_de_condicoes(["Agarrado"])
    assert m["ataque"] == -2
    assert m["ca"] == -5


def test_modificadores_enredado_vulneravel() -> None:
    m = modificadores_de_condicoes(["Enredado"])
    assert m["ataque"] == -2
    assert m["ca"] == -2


def test_modificadores_sem_duplicar_implica() -> None:
    m = modificadores_de_condicoes(["Cego", "Surpreendido"])
    assert m["ca"] == -5


def test_modificadores_legacy_mb_alias() -> None:
    m = modificadores_de_condicoes_mb(["Cego", "Surpreso"])
    assert m["ca"] == -5


def test_resolver_entrada_por_nome() -> None:
    row = resolver_entrada_condicao("Vulnerável")
    assert row is not None
    assert row.get("slug") == "vulneravel"


def test_armas_overlay_lote4_total() -> None:
    assert len(lista_armas_v13_overlay()) >= 56
