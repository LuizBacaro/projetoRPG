"""Testes unitários das regras de familiar D&D 3.5."""

from app.games.dnd35.rules.familiar import (
    calcular_derivadas_familiar,
    elegibilidade_familiar,
    niveis_familiar_classe,
)


def test_elegibilidade_mago_e_feiticeiro():
    ok, _, nm = elegibilidade_familiar("Mago", 5)
    assert ok and nm == 5
    ok2, _, nm2 = elegibilidade_familiar("Feiticeiro", 3)
    assert ok2 and nm2 == 3


def test_multiclasse_mago_feiticeiro_soma_niveis():
    assert niveis_familiar_classe("Mago 3 / Feiticeiro 2", 10) == 5


def test_druida_nao_elegivel_familiar():
    ok, motivo, _ = elegibilidade_familiar("Druida", 7)
    assert not ok
    assert "Mago" in motivo or "Feiticeiro" in motivo


def test_calcular_hp_metade_mestre():
    deriv = calcular_derivadas_familiar(
        nivel_mestre=3,
        hp_maximo_mestre=9,
        atributos_base={"destreza": 15, "forca": 10, "constituicao": 10},
    )
    assert deriv["hp_max_sugerido"] == 4
    assert deriv["inteligencia"] == 7
    assert "transmitir_magias_toque" in deriv["habilidades_especiais"]
