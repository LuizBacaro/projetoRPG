"""Testes Duende — Heróis de Arton HA-1."""

from __future__ import annotations

from app.games.tormenta.rules.duende_t20 import (
    calcular_duende,
    calcular_modificadores_atributos_duende,
    calcular_tracos_duende,
    lista_presentes_duende,
    opcoes_duende_catalogo,
    presentes_duende_slugs_ficha,
    validar_duende_ficha,
)
from app.games.tormenta.rules.poderes_ficha_v13_t20 import listar_poderes_sync_v13
from app.games.tormenta.rules.progressao_pv_t20 import pm_bonus_racial_ha_de_ficha
from app.games.tormenta.rules.racas_t20 import lista_racas_herois_arton
from app.games.tormenta.rules.tracos_raciais_t20 import preview_tracos_raciais


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
    assert op["patamares_troca_poder"] == [5, 10, 15, 20]


def test_calcular_tracos_duende_mineral_e_tabu() -> None:
    cfg = {
        "natureza": "mineral",
        "tamanho_raca": "pequeno",
        "presentes": ["visao_feerica", "voo", "lingua_da_natureza"],
        "tabu_penalidade": "diplomacia",
        "tabu_texto": "Nunca mente",
    }
    tr = calcular_tracos_duende(cfg)
    assert tr["ca_bonus"] == 1
    assert tr["reducao_dano"]["corte"] == 5
    assert tr["pericias_bonus"]["Diplomacia"] == -5
    assert tr["pericias_bonus"]["Adestramento"] == 2
    assert tr["sentidos_misticos"] is True
    assert tr["deslocamento_pairar_m"] == 9


def test_preview_duende_com_config_completa() -> None:
    du = _ficha_duende_minima()["duende"]
    p = preview_tracos_raciais("duende", regra_versao="v13", duende_config=du)
    assert p["encontrado"] is True
    assert any("Tabu" in x for x in p["escolhas_resumo"])
    assert any("Limitação:" in x for x in p["escolhas_resumo"])


def test_pm_bonus_duende_geracao_aleatoria() -> None:
    fj = {
        "game_suplemento": "herois_arton",
        "raca_tormenta_slug": "duende",
        "duende": {"geracao_aleatoria": True},
    }
    assert pm_bonus_racial_ha_de_ficha(fj, 1) == 2


def test_presentes_sync_v13() -> None:
    fj = {
        "regra_versao": "v13",
        "raca_tormenta_slug": "duende",
        "duende": _ficha_duende_minima()["duende"],
    }
    sync = listar_poderes_sync_v13(fj)
    assert len(sync) == 3
    assert all("presente_duende" in s["notas"] for s in sync)


def test_troca_poder_por_presente_validacao() -> None:
    f = _ficha_duende_minima(
        duende={"trocas_poder_presente": [{"nivel": 4, "presente": "voo"}]}
    )
    ok, msg = validar_duende_ficha(f)
    assert not ok
    assert "patamar" in msg.lower() or "5" in msg


def test_troca_poder_presente_ok() -> None:
    f = _ficha_duende_minima(
        duende={
            "trocas_poder_presente": [{"nivel": 10, "presente": "sonhos_profeticos"}],
            "presentes_opcoes": {},
        }
    )
    ok, msg = validar_duende_ficha(f)
    assert ok, msg
    slugs = presentes_duende_slugs_ficha(f)
    assert "sonhos_profeticos" in slugs


def test_calcular_duende_resumo() -> None:
    data = calcular_duende(_ficha_duende_minima())
    assert data is not None
    assert data["valido"] is True
    assert data["tracos"]["presentes_ativos"]
    assert len(data["limitacoes_fixas"]) >= 3


def test_troca_patamar_duplicado() -> None:
    f = _ficha_duende_minima(
        duende={
            "trocas_poder_presente": [
                {"nivel": 10, "presente": "sonhos_profeticos"},
                {"nivel": 10, "presente": "voo"},
            ]
        }
    )
    ok, msg = validar_duende_ficha(f)
    assert not ok
    assert "duplicado" in msg.lower()


def test_calcular_tracos_inclui_presente_da_troca() -> None:
    cfg = {
        "tamanho_raca": "medio",
        "natureza": "vegetal",
        "presentes": ["invisibilidade", "lingua_da_natureza", "sonhos_profeticos"],
        "trocas_poder_presente": [{"nivel": 10, "presente": "voo"}],
        "tabu_penalidade": "diplomacia",
    }
    tr = calcular_tracos_duende(cfg)
    assert tr.get("voo_pm_por_rodada") == 1
    slugs = {p["slug"] for p in tr["presentes_ativos"]}
    assert "voo" in slugs
