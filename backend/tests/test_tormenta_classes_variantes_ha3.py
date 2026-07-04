"""HA-3 — Classes variantes e origens Heróis de Arton."""

from __future__ import annotations

from app.games.tormenta.rules.classes_t20 import (
    lista_classes_herois_arton,
    validar_classe_variante,
    validar_compatibilidade_classes_v13,
)
from app.games.tormenta.rules.origens_t20 import (
    lista_origens_com_suplemento,
    lista_origens_herois_arton,
    origem_por_slug,
    validar_beneficios_origem,
)
from app.games.tormenta.rules.regra_versao_t20 import SUPLEMENTO_HEROIS_ARTON


def test_quatorze_classes_variantes() -> None:
    rows = lista_classes_herois_arton()
    variantes = [r for r in rows if r["slug"] != "treinador"]
    assert len(variantes) == 14
    com_base = [r for r in variantes if r.get("classe_variante_base")]
    assert len(com_base) == 13
    duelista = next(r for r in variantes if r["slug"] == "duelista")
    assert duelista.get("classe_variante_base") is None


def test_validar_classe_variante_alquimista_vs_inventor() -> None:
    err = validar_classe_variante("alquimista", ["inventor"])
    assert err is not None
    assert "incompatível" in err.lower() or "incompat" in err.lower()


def test_validar_classe_variante_ok_sem_conflito() -> None:
    assert validar_classe_variante("alquimista", ["guerreiro"]) is None
    assert validar_classe_variante("guerreiro", ["alquimista"]) is None


def test_validar_compatibilidade_ficha_multiclasse() -> None:
    ficha_ok = {
        "regra_versao": "v13",
        "tormenta_classe_mb_slug": "alquimista",
        "multiclasse_v13": [{"slug": "alquimista", "nivel": 3}],
    }
    assert validar_compatibilidade_classes_v13(ficha_ok, 3) is None

    ficha_bad = {
        "regra_versao": "v13",
        "tormenta_classe_mb_slug": "inventor",
        "multiclasse_v13": [
            {"slug": "inventor", "nivel": 2},
            {"slug": "alquimista", "nivel": 1},
        ],
    }
    err = validar_compatibilidade_classes_v13(ficha_bad, 3)
    assert err is not None


def test_origens_herois_arton_quatorze() -> None:
    rows = lista_origens_herois_arton()
    assert len(rows) == 14
    assert all(r["fonte_catalogo"] == SUPLEMENTO_HEROIS_ARTON for r in rows)


def test_origens_com_suplemento_mescla() -> None:
    core = lista_origens_com_suplemento()
    ha = lista_origens_com_suplemento(SUPLEMENTO_HEROIS_ARTON)
    assert len(ha) == len(core) + 14


def test_origem_por_slug_bacharel() -> None:
    row = origem_por_slug("bacharel")
    assert row is not None
    assert row["nome"] == "Bacharel"
    assert row.get("troca_pericia_treinada") is True


def test_validar_beneficios_origem_herois() -> None:
    ok, _ = validar_beneficios_origem(
        "bacharel",
        ["pericia:conhecimento", "poder:retórica"],
    )
    assert ok is True
