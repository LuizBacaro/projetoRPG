"""HA-2 — Classe Treinador, Melhor Amigo e Domar Criatura."""

from __future__ import annotations

from app.games.tormenta.rules.classes_t20 import (
    classe_por_slug,
    lista_classes_com_suplemento,
    lista_classes_herois_arton,
)
from app.games.tormenta.rules.domar_criatura_t20 import (
    dano_domar,
    dano_domar_por_nivel,
    resolver_domar,
)
from app.games.tormenta.rules.melhor_amigo_t20 import (
    calcular_melhor_amigo,
    lista_tipos_melhor_amigo,
    qtd_truques_por_nivel,
    truques_disponiveis,
    validar_melhor_amigo_ficha,
)
from app.games.tormenta.rules.pericias_classe_t20 import (
    config_pericias_classe_v13,
    vagas_classe_v13,
)
from app.games.tormenta.rules.progressao_pv_t20 import preview_pv_mb
from app.games.tormenta.rules.regra_versao_t20 import SUPLEMENTO_HEROIS_ARTON


def test_treinador_no_catalogo_herois_arton() -> None:
    rows = lista_classes_herois_arton()
    slugs = {r["slug"] for r in rows}
    assert "treinador" in slugs
    assert len(rows) == 15


def test_treinador_aparece_com_suplemento() -> None:
    core = lista_classes_com_suplemento("v13")
    ha = lista_classes_com_suplemento("v13", SUPLEMENTO_HEROIS_ARTON)
    assert len(ha) == len(core) + 15
    tre = next(c for c in ha if c["slug"] == "treinador")
    assert tre["fonte_catalogo"] == SUPLEMENTO_HEROIS_ARTON
    assert tre.get("pm_por_nivel") == 4


def test_classe_por_slug_encontra_treinador() -> None:
    row = classe_por_slug("treinador", "v13")
    assert row is not None
    assert row["pv_inicial"] == 12
    assert row["pv_por_nivel"] == 3


def test_treinador_pericias_classe_config() -> None:
    cfg = config_pericias_classe_v13("treinador")
    assert cfg is not None
    assert cfg["pericias_fixas"] == ["adestramento", "vontade"]
    assert cfg["pericias_escolha_qtd"] == 4
    assert vagas_classe_v13("treinador") == 6


def test_preview_pv_treinador() -> None:
    prev = preview_pv_mb("treinador", 1, 2, regra_versao="v13")
    assert prev["encontrado"] is True
    assert prev["pv_max"] == 14  # 12 + CON 2 (v1.3 usa valor bruto)


def test_truques_disponiveis_por_nivel() -> None:
    nv1 = truques_disponiveis(1)
    nv5 = truques_disponiveis(5)
    assert len(nv1) >= 8
    assert len(nv5) >= len(nv1)
    assert all(t["nivel_minimo"] <= 5 for t in nv5)
    assert qtd_truques_por_nivel(1) == 2
    assert qtd_truques_por_nivel(4) == 3
    assert qtd_truques_por_nivel(10) == 5


def test_tipos_melhor_amigo_cinco() -> None:
    tipos = lista_tipos_melhor_amigo()
    assert len(tipos) == 5
    slugs = {t["slug"] for t in tipos}
    assert slugs == {"animal", "construto", "espirito", "monstro", "morto_vivo"}


def test_calcular_melhor_amigo_valido() -> None:
    ficha = {
        "regra_versao": "v13",
        "tormenta_classe_mb_slug": "treinador",
        "nivel": 1,
        "melhor_amigo": {
            "nome": "Rex",
            "tipo": "animal",
            "truques": ["alado", "amigao"],
            "nivel": 1,
        },
    }
    ok, _ = validar_melhor_amigo_ficha(ficha)
    assert ok is True
    res = calcular_melhor_amigo(ficha)
    assert res is not None
    assert res["valido"] is True
    assert res["nome"] == "Rex"
    assert res["bonus_tipo"]["bonus_atributos"]["for"] == 1


def test_melhor_amigo_rejeita_pre_requisito() -> None:
    ficha = {
        "regra_versao": "v13",
        "tormenta_classe_mb_slug": "treinador",
        "melhor_amigo": {
            "nome": "Falcão",
            "tipo": "animal",
            "truques": ["asas_aliadas"],
        },
    }
    ok, motivo = validar_melhor_amigo_ficha(ficha)
    assert ok is False
    assert "asas_aliadas" in motivo


def test_dano_domar_por_nivel() -> None:
    assert dano_domar_por_nivel(1) == "0"
    assert dano_domar(2) == "2d8"
    assert dano_domar_por_nivel(6) == "4d8"
    assert dano_domar_por_nivel(18) == "10d8"


def test_resolver_domar() -> None:
    res = resolver_domar(15, 10, 6)
    assert res["sucesso"] is True
    assert res["dado_dano"] == "4d8"
    assert res["pode_controlar"] is True
    falha = resolver_domar(8, 12, 3)
    assert falha["sucesso"] is False
