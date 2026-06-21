"""Infraestrutura aplicar_feat_efeito."""

from app.games.dnd5e.rules.feat_efeitos import (
    agregar_efeitos_feats,
    aplicar_feat_efeito,
    bonus_ataque_feats,
)
from app.games.dnd5e.rules.ficha import montar_resumo_ficha
from app.games.dnd5e.rules.progressao import bonus_hp_por_nivel_feat


def test_alert_bonus_iniciativa_ficha():
    fx = aplicar_feat_efeito("alert", "ficha_preview")
    assert fx["bonus_iniciativa"] == 5


def test_tough_via_agregar_progressao():
    fx = agregar_efeitos_feats(["tough"], "progressao")
    assert fx["bonus_hp_por_nivel"] == 2
    assert bonus_hp_por_nivel_feat(["tough"]) == 2


def test_archery_somente_distancia():
    assert bonus_ataque_feats(["archery"], distancia=True) == 2
    assert bonus_ataque_feats(["archery"], corpo_a_corpo=True) == 0


def test_ficha_preview_iniciativa_com_alert():
    base = {
        k: 10
        for k in (
            "strength",
            "dexterity",
            "constitution",
            "intelligence",
            "wisdom",
            "charisma",
        )
    }
    res = montar_resumo_ficha(
        raca_slug="humano",
        classe_slug="guerreiro",
        scores_base=base,
        pericias_classe_escolhidas=["atletismo", "intimidacao"],
        feats=["alert"],
    )
    assert res["iniciativa"] == 5
    assert res["efeitos_feats"]["bonus_iniciativa"] == 5
