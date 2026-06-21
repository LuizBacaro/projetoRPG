"""Feats combate/magia tier 1 e ações PHB (D5E-041/042/051/052)."""

from app.games.dnd5e.rules.combate import (
    EconomiaTurno,
    gastar_acao_turno,
    resumo_modificadores_ataque,
)
from app.games.dnd5e.rules.feat_combate import (
    bonus_iniciativa_feats,
    resolver_salvamento_com_feats,
    war_caster_vantagem_concentracao,
)
from app.games.dnd5e.rules.ficha import montar_resumo_ficha
from app.games.dnd5e.rules.magia import Conjurador
from app.games.dnd5e.rules.magia import teste_concentracao as roll_teste_concentracao
from app.games.dnd5e.rules.oportunidade import (
    resolver_ataque_oportunidade,
    validar_oportunidade,
)


def test_alert_bonus_iniciativa():
    assert bonus_iniciativa_feats(["alert"]) == 5


def test_observant_passiva_ficha():
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
        feats=["observant"],
    )
    assert res["percepcao_passiva"] == 15
    assert res["investigacao_passiva"] == 15


def test_resilient_proficiencia_save():
    out = resolver_salvamento_com_feats(
        2,
        2,
        12,
        proficiente=False,
        feats=["resilient"],
        feat_escolhas={"resilient": "constitution"},
        save_tipo="fortitude",
        rolagem_d20=8,
    )
    assert out["proficiente_resilient"] is True
    assert out["total"] == 12
    assert out["sucesso"] is True


def test_lucky_reroll_salvamento():
    out = resolver_salvamento_com_feats(
        0,
        2,
        15,
        proficiente=True,
        feats=["lucky"],
        rolagem_d20=5,
        usar_lucky=True,
        lucky_restantes=3,
        rng=lambda a, b: 18,
    )
    assert out["lucky_reroll"] == 18
    assert out["lucky_restantes"] == 2
    assert out["sucesso"] is True


def test_war_caster_concentracao_vantagem():
    assert war_caster_vantagem_concentracao(["war-caster"]) is True
    conj = Conjurador(
        conjurador_id="1",
        nome="X",
        classe="mago",
        nivel=1,
        mod_habilidade=2,
        bonus_proficiencia=2,
        magia_concentracao="1",
    )
    ok = roll_teste_concentracao(
        conj,
        20,
        2,
        rolagem_d20=8,
        rolagem_secundaria=16,
        bonus_proficiencia=2,
    )
    assert ok is True


def test_economia_dash_dodge_disengage_help():
    eco = EconomiaTurno()
    dash = gastar_acao_turno(eco, "dash")
    assert dash.acao_usada is True
    assert dash.velocidade_metros == 18.0

    eco2 = gastar_acao_turno(EconomiaTurno(), "dodge")
    assert eco2.esquivando is True

    eco3 = gastar_acao_turno(EconomiaTurno(), "disengage")
    assert eco3.desengajado is True

    eco4 = gastar_acao_turno(EconomiaTurno(), "help", ajuda_alvo_id="alvo-1")
    assert eco4.ajuda_alvo_id == "alvo-1"


def test_dodge_desvantagem_ataque():
    mod = resumo_modificadores_ataque([], ["esquivando"], corpo_a_corpo=True)
    assert mod.desvantagem is True


def test_oportunidade_bloqueia_desengajado():
    try:
        validar_oportunidade(EconomiaTurno(), alvo_desengajado=True)
        assert False, "deveria falhar"
    except ValueError as e:
        assert "Desengajar" in str(e)


def test_oportunidade_consume_reacao():
    res = resolver_ataque_oportunidade(
        str_mod=3,
        dex_mod=1,
        bonus_proficiencia=2,
        ac_alvo=10,
        rolagem_d20=15,
        economia_atacante=EconomiaTurno(),
    )
    assert res["acerto"] is True
    assert res["economia_atacante"]["reacao_usada"] is True
