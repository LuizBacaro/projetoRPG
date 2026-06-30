"""Benefícios globais por nível — v1.3 vs MB."""

from __future__ import annotations

from app.games.tormenta.rules.beneficios_nivel_t20 import (
    beneficio_nivel,
    graduacao_pericias_texto_v13,
    lista_beneficios_por_nivel,
    lista_beneficios_por_nivel_mb,
)


def test_beneficio_v13_nivel_1_graduacao() -> None:
    ben = beneficio_nivel(1, "v13")
    assert ben is not None
    assert ben["graduacao_pericias"] == "+2/+0"
    assert ben["xp_total"] == 0
    assert ben["poderes_gerais_totais"] == 1
    assert ben["talentos_totais"] == 1


def test_beneficio_v13_nivel_7_graduacao() -> None:
    ben = beneficio_nivel(7, "v13")
    assert ben is not None
    assert ben["graduacao_pericias"] == "+7/+3"
    assert ben["xp_total"] == 21000


def test_beneficio_v13_nivel_20_xp() -> None:
    ben = beneficio_nivel(20, "v13")
    assert ben is not None
    assert ben["xp_total"] == 190000
    assert ben["poderes_gerais_totais"] == 10


def test_graduacao_texto_v13_bate_json() -> None:
    for nv in range(1, 21):
        ben = beneficio_nivel(nv, "v13")
        assert ben is not None
        assert graduacao_pericias_texto_v13(nv) == ben["graduacao_pericias"]


def test_lista_v13_vinte_niveis() -> None:
    rows = lista_beneficios_por_nivel("v13")
    assert len(rows) == 20
    assert rows[0]["nivel"] == 1
    assert rows[-1]["nivel"] == 20


def test_regressao_mb_nivel_1_inalterada() -> None:
    ben_mb = beneficio_nivel(1, "mb")
    assert ben_mb is not None
    assert ben_mb["graduacao_pericias"] == "+4/+0"
    assert ben_mb["talentos_totais"] == 1
    assert "poderes_gerais_totais" not in ben_mb


def test_regressao_mb_lista_compat() -> None:
    assert lista_beneficios_por_nivel_mb() == lista_beneficios_por_nivel("mb")
