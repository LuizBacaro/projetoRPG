"""Regras D&D 5E — combate."""

from app.games.dnd5e.rules.combate import (
    ArmaCombate,
    Combatente,
    RodadaCombate,
    StatusVida,
    aplicar_dano_hp,
    aplicar_teste_morte,
    ataque_atinge_ca,
    calcular_dano,
    calcular_iniciativa,
    estabilizar_combatente,
    registrar_teste_morte,
    resolver_ataque,
    resumo_modificadores_ataque,
    verificar_morte,
)


def test_iniciativa_ordenacao() -> None:
    g = Combatente("g", "Guerreiro", hp=30, max_hp=30, ac=16, dex_mod=1, str_mod=3)
    gob = Combatente("b", "Goblin", hp=8, max_hp=8, ac=15, dex_mod=2, str_mod=0)
    rodada = RodadaCombate(combatentes=[g, gob])
    rodada.ordenar_por_iniciativa(rolagens={"g": 12, "b": 8})
    assert rodada.ordem_iniciativa[0].nome == "Guerreiro"
    assert rodada.ordem_iniciativa[0].iniciativa_rolagem == 13


def test_ataque_atinge_ca() -> None:
    assert ataque_atinge_ca(3, 2, 16, rolagem_d20=16) is True
    assert ataque_atinge_ca(3, 2, 16, rolagem_d20=10) is False


def test_critico_multiplica_dados() -> None:
    arma = ArmaCombate(dano="1d8")
    normal = calcular_dano(arma, 3, is_critico=False, rng=lambda a, b: 6)
    crit = calcular_dano(arma, 3, is_critico=True, rng=lambda a, b: 6)
    assert crit >= normal
    assert crit == max(1, 6 + 6 + 3)


def test_morte_tres_falhas() -> None:
    c = Combatente("x", "Alvo", hp=0, max_hp=10, ac=10)
    assert verificar_morte(0, 0, 0) == StatusVida.INCONSCIENTE
    c.death_failures = 2
    status = registrar_teste_morte(c, 5)
    assert status == StatusVida.MORTO
    assert c.death_failures >= 3


def test_calcular_iniciativa() -> None:
    assert calcular_iniciativa(2, rolagem_d20=10) == 12


def test_condicao_cego_desvantagem() -> None:
    mods = resumo_modificadores_ataque(["cego"], [])
    assert mods.desvantagem is True
    assert mods.vantagem is False


def test_condicao_alvo_atordoado_vantagem() -> None:
    mods = resumo_modificadores_ataque([], ["atordoado"])
    assert mods.vantagem is True


def test_condicao_incapacitado_acerto_automatico_corpo_a_corpo() -> None:
    mods = resumo_modificadores_ataque([], ["incapacitado"], corpo_a_corpo=True)
    assert mods.acerto_automatico is True
    assert mods.critico_automatico is True


def test_resolver_ataque_incapacitado_acerta_sem_rolar() -> None:
    r = resolver_ataque(
        0,
        2,
        30,
        rolagem_d20=3,
        condicoes_alvo=["incapacitado"],
        corpo_a_corpo=True,
    )
    assert r.acerto_automatico is True
    assert r.acerto is True


def test_vantagem_e_desvantagem_cancelam() -> None:
    mods = resumo_modificadores_ataque(["cego"], ["atordoado"])
    v, d = mods.rolagem_efetiva()
    assert v is False and d is False


def test_resolver_ataque_nat_20_critico_e_acerto() -> None:
    r = resolver_ataque(3, 2, 30, rolagem_d20=20)
    assert r.is_critico is True
    assert r.acerto is True


def test_aplicar_teste_morte_nat_20_recupera_1_pv() -> None:
    r = aplicar_teste_morte(0, 0, 0, 20)
    assert r.hp_atual == 1
    assert r.death_successes == 0
    assert r.death_failures == 0
    assert r.status == StatusVida.VIVO


def test_dano_em_zero_adiciona_falha() -> None:
    r = aplicar_dano_hp(0, 30, 0, 0, 5)
    assert r.death_failures == 1
    assert r.status == StatusVida.INCONSCIENTE


def test_dano_critico_em_zero_duas_falhas() -> None:
    r = aplicar_dano_hp(0, 30, 0, 0, 5, is_critico=True)
    assert r.death_failures == 2


def test_morte_instantanea_dano_excedente() -> None:
    r = aplicar_dano_hp(5, 10, 0, 0, 20)
    assert r.morte_instantanea is True
    assert r.status == StatusVida.MORTO


def test_estabilizado_volta_a_morrer_com_dano() -> None:
    r = aplicar_dano_hp(0, 20, 0, 3, 3, status_vida=StatusVida.ESTABILIZADO)
    assert r.death_successes == 0
    assert r.death_failures == 1
    assert r.status == StatusVida.INCONSCIENTE


def test_estabilizar_medicina_cd10() -> None:
    ok = estabilizar_combatente(0, metodo="medicina", rolagem_d20=12, mod_medicina=0)
    assert ok.sucesso is True
    assert ok.status == StatusVida.ESTABILIZADO
    fail = estabilizar_combatente(0, metodo="medicina", rolagem_d20=4, mod_medicina=0)
    assert fail.sucesso is False


def test_gastar_economia_acao_duplicada_falha() -> None:
    from app.games.dnd5e.rules.combate import gastar_acao_turno, reset_economia_turno

    eco = gastar_acao_turno(reset_economia_turno(), "acao")
    try:
        gastar_acao_turno(eco, "acao")
        assert False, "deveria falhar"
    except ValueError:
        pass
