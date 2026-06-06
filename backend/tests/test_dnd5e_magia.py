"""Regras D&D 5E — magia."""

from app.games.dnd5e.rules.magia import (
    Conjurador,
    Magia,
    calcular_dc_magia,
    escalar_expressao_dano_truque,
    espacos_por_classe_nivel,
    lancar_magia,
    max_nivel_magia_conjuravel,
    pontos_feiticaria_max,
    recuperar_espacos_repouso_longo,
    salvaguarda_atinge_dc,
    truque_multiplicador_dados,
)
from app.games.dnd5e.services.conjuracao_shared import perfil_conjuracao_classe


def test_dc_calcula() -> None:
    assert calcular_dc_magia(3, 4) == 15


def test_espacos_recuperam_repouso_longo() -> None:
    c = Conjurador(
        conjurador_id="m1",
        nome="Mago",
        classe="mago",
        nivel=5,
        mod_habilidade=4,
        bonus_proficiencia=3,
    )
    magia = Magia("bola-fogo", "Bola de Fogo", nivel=3)
    assert lancar_magia(c, magia) is True
    assert c.espacos_disponiveis(3) == 1
    recuperar_espacos_repouso_longo(c)
    assert c.espacos_disponiveis(3) == 2


def test_salvaguarda_atinge_dc() -> None:
    assert salvaguarda_atinge_dc(2, 15, rolagem_d20=14) is True
    assert salvaguarda_atinge_dc(2, 15, rolagem_d20=10) is False


def test_bardo_slots_reduzidos_vs_mago() -> None:
    bardo20 = espacos_por_classe_nivel("bardo", 20)
    mago20 = espacos_por_classe_nivel("mago", 20)
    assert bardo20[6] == 4
    assert bardo20[7] == 0
    assert mago20[9] == 4
    assert max_nivel_magia_conjuravel("bardo", 20) == 6
    assert max_nivel_magia_conjuravel("mago", 20) == 9


def test_perfil_conjuracao_feiticeiro_conhecido() -> None:
    perfil = perfil_conjuracao_classe("feiticeiro", 5, mod_habilidade=3)
    assert perfil["modo_lista"] == "conhecido"
    assert perfil["habilidade_primaria"] == "cha"
    assert perfil["magias_conhecidas_max"] == 6


def test_truque_escala_dados_por_nivel() -> None:
    assert truque_multiplicador_dados(4) == 1
    assert truque_multiplicador_dados(5) == 2
    assert truque_multiplicador_dados(11) == 3
    assert escalar_expressao_dano_truque("1d10", 5) == "2d10"
    assert escalar_expressao_dano_truque("1d10", 17) == "4d10"


def test_pontos_feiticaria_max() -> None:
    assert pontos_feiticaria_max("feiticeiro", 1) == 0
    assert pontos_feiticaria_max("feiticeiro", 5) == 5
    assert pontos_feiticaria_max("mago", 5) == 0
