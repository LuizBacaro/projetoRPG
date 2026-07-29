"""Testes do motor de efeitos estruturados na ficha (Heróis de Arton)."""

from app.games.tormenta.rules.efeitos_ficha_t20 import (
    agregar_efeitos_ficha,
    efeitos_de_origem,
    normalizar_efeito,
)
from app.games.tormenta.rules.origens_t20 import lista_origens_herois_arton


def test_lista_origens_ha_tem_30():
    assert len(lista_origens_herois_arton()) >= 30


def test_naufrago_pv_pm():
    fj = {"origem_slug": "naufrago", "regra_versao": "v13"}
    agg = agregar_efeitos_ficha(fj)
    tot = agg["totais"]
    assert tot["pv_max"] == 5
    assert tot["pm_max"] == 2
    rotulos = [f["rotulo"] for f in agg["fontes"]]
    assert any("Náufrago" in r and "PV" in r for r in rotulos)
    habilidade = next(a for a in agg["ativos"] if a.get("id") == "adaptacao")
    assert habilidade["tipo_ativo"] == "habilidade_origem"
    assert habilidade["custo_pm"] == 2
    assert habilidade["duracao"] == "cena"


def test_contrabandista_carga_e_ocultar():
    fj = {"origem_slug": "contrabandista"}
    agg = agregar_efeitos_ficha(fj)
    tot = agg["totais"]
    assert tot["carga_espacos"] == 2
    per = tot["pericias"]
    assert per.get("ladinagem") == 5


def test_defesa_armada_condicional():
    ef = normalizar_efeito(
        {
            "id": "da_def",
            "alvo": "defesa",
            "valor": 2,
            "quando": "arma_duas_maos",
            "rotulo": "Defesa Armada +2",
        },
        fonte_tipo="poder",
        fonte_slug="defesa_armada",
    )
    assert ef is not None
    agg_sem = agregar_efeitos_ficha(
        {"poderes_slugs": ["defesa_armada"]},
        poderes_slugs=["defesa_armada"],
        contexto={},
    )
    assert agg_sem["totais"]["defesa"] == 0
    agg_com = agregar_efeitos_ficha(
        {},
        poderes_slugs=["defesa_armada"],
        contexto={"arma_duas_maos": True},
    )
    assert agg_com["totais"]["defesa"] == 2


def test_mensageiro_deslocamento():
    efs = efeitos_de_origem("mensageiro")
    assert any(e.get("alvo") == "deslocamento_m" and e.get("valor") == 3 for e in efs)
