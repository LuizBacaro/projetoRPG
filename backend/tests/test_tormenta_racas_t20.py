"""Raças MB — carregamento e ajustes."""

from app.games.tormenta.rules.racas_t20 import lista_racas_mb


def test_lista_racas_tamanho_e_anao() -> None:
    lst = lista_racas_mb()
    assert len(lst) == 11
    anao = next(x for x in lst if x["slug"] == "anao")
    assert anao["nome"] == "Anão"
    assert anao["ajustes"]["con"] == 4
    assert anao["ajustes"]["sab"] == 2
    assert anao["ajustes"]["des"] == -2
    hum = next(x for x in lst if x["slug"] == "humano")
    assert hum["escolhe_duas_mais2"] is True
    lef = next(x for x in lst if x["slug"] == "lefou")
    assert lef["mod_car_fixo"] == -4
    orc = next(x for x in lst if x["slug"] == "meio_orc")
    assert orc["escolhe_um_mais2"] is True
    assert "int" in orc["excluir_atributos_mais2"]
    assert "car" in orc["excluir_atributos_mais2"]
