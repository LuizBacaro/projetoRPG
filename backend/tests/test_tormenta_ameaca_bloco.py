"""Testes unitários — bloco de Ameaça Tormenta (RF-T13)."""

from __future__ import annotations

from app.games.tormenta.rules.ameaca_bloco_t20 import (
    ameaca_minima,
    consolidar_ameaca_de_personagem,
    limpar_texto_override,
    modificador_atributo,
    montar_bloco_ameaca,
    obter_nd,
    obter_papel_combate,
)


def _snap_monstro(**kwargs):
    base = {
        "nome": "Goblin Espadachim",
        "nivel": 1,
        "ca": 16,
        "pv_max": 8,
        "pa_max": 0,
        "rd": "",
        "iniciativa": 2,
        "deslocamento": "9m",
        "tamanho": "Pequeno",
        "fort_total": 1,
        "ref_total": 3,
        "von_total": 0,
        "for_valor": 12,
        "des_valor": 14,
        "con_valor": 12,
        "int_valor": 10,
        "sab_valor": 10,
        "car_valor": 8,
    }
    base.update(kwargs)
    return base


def test_modificador_atributo():
    assert modificador_atributo(10) == 0
    assert modificador_atributo(14) == 2
    assert modificador_atributo(8) == -1


def test_montar_bloco_monstro_basico():
    fj = {
        "nd": 1,
        "tipo_criatura": "Humanoide",
        "ataques": [
            {
                "nome": "Cimitarra",
                "bonus_ataque": "+3",
                "dano": "1d6+1",
                "critico": "18-20",
            }
        ],
        "ameaca": {
            "papel_combate": "lacaio",
            "percepcao": 2,
            "sentidos": "visão na penumbra",
            "pericias_fortes": [{"nome": "Furtividade", "bonus": 6}],
        },
    }
    texto, fonte = montar_bloco_ameaca(_snap_monstro(), ficha_json=fj)
    assert fonte == "gerado"
    assert "Goblin Espadachim ND 1" in texto
    assert "Humanoide Pequeno" in texto
    assert "Defesa 16" in texto
    assert "Pontos de Vida 8, Pontos de Mana 0" in texto
    assert "Cimitarra +3" in texto
    assert "For +1" in texto
    assert "Des +2" in texto
    assert "Car -1" in texto
    assert "Furtividade +6" in texto
    assert "visão na penumbra" in texto


def test_texto_override_prevalece():
    fj = {"ameaca": {"texto_override": "Bloco manual do mestre"}}
    texto, fonte = montar_bloco_ameaca(_snap_monstro(), ficha_json=fj)
    assert fonte == "override"
    assert texto == "Bloco manual do mestre"


def test_limpar_override_regenera():
    fj = {
        "ameaca": {"nd": 2, "texto_override": "manual"},
        "ataques": [{"nome": "Mordida", "bonus_ataque": "+5", "dano": "1d6"}],
    }
    fj2 = limpar_texto_override(fj)
    texto, fonte = montar_bloco_ameaca(
        _snap_monstro(nome="Lobo", nivel=2), ficha_json=fj2
    )
    assert fonte == "gerado"
    assert "Lobo ND 2" in texto
    assert "Mordida +5" in texto


def test_atributos_nulos():
    fj = {"ameaca": {"atributos_nulos": ["con"], "nd": 3}}
    texto, _ = montar_bloco_ameaca(_snap_monstro(nome="Golem"), ficha_json=fj)
    assert "Con —" in texto


def test_papel_default_especial_com_pm():
    assert obter_papel_combate({"pa_max": 12}, {}) == "especial"
    assert obter_papel_combate({"pa_max": 0}, {}) == "solo"


def test_obter_nd_legado_e_ameaca():
    assert obter_nd({"nivel": 5}, {"ameaca": {"nd": 4}}) == 4
    assert obter_nd({"nivel": 5}, {"nd": 2}) == 2
    assert obter_nd({"nivel": 7}, {}) == 7


def test_consolidar_ameaca_de_personagem():
    snap = _snap_monstro(pa_max=10, nivel=3, nome="Mago Vilão")
    fj = {
        "ataques": [{"nome": "Cajado", "bonus_ataque": "+2", "dano": "1d6"}],
        "pericias": [
            {"nome": "Misticismo", "total": 9},
            {"nome": "Percepção", "total": 5},
        ],
    }
    magias = [{"nome": "Bola de Fogo", "circulo": 3}]
    out = consolidar_ameaca_de_personagem(
        snap, ficha_json=fj, magias_vinculos=magias, papel_combate="especial"
    )
    am = out["ameaca"]
    assert am["nd"] == 3
    assert am["papel_combate"] == "especial"
    assert am["texto_override"] is None
    assert am["acoes"]["corpo_a_corpo"][0]["nome"] == "Cajado"
    assert any(m["nome"] == "Bola de Fogo" for m in am["acoes"]["magias"])
    assert any(p["nome"] == "Misticismo" for p in am["pericias_fortes"])


def test_ameaca_minima():
    am = ameaca_minima(nd=2, papel_combate="lacaio")
    assert am["nd"] == 2
    assert am["papel_combate"] == "lacaio"
    assert am["acoes"]["corpo_a_corpo"] == []
