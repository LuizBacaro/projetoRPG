"""Raças Tormenta 20 v1.3 — catálogo, traços e Versátil."""

from __future__ import annotations

from app.games.tormenta.rules.pericias_criacao_t20 import (
    pericias_treinadas_extra_raca,
    vagas_pericias_treinadas,
)
from app.games.tormenta.rules.racas_t20 import lista_racas
from app.games.tormenta.rules.tracos_raciais_t20 import (
    humano_versatil_pericias_extra,
    preview_tracos_raciais,
    tracos_mecanicos_por_slug,
)


def test_lista_racas_v13_dezessete() -> None:
    lst = lista_racas("v13")
    assert len(lst) == 17
    slugs = {r["slug"] for r in lst}
    assert "hynne" in slugs
    assert "dahllan" in slugs
    assert "gnomo" not in slugs
    assert "meio_elfo" not in slugs


def test_humano_v13_escolhe_tres_mais1() -> None:
    hum = next(x for x in lista_racas("v13") if x["slug"] == "humano")
    assert hum["escolhe_tres_mais1"] is True
    assert hum["escolhe_duas_mais2"] is False
    assert hum["pericias_treinadas_extra"] == 2


def test_lefou_v13_exclui_car() -> None:
    lef = next(x for x in lista_racas("v13") if x["slug"] == "lefou")
    assert lef["escolhe_tres_mais1"] is True
    assert "car" in lef["excluir_atributos_mais1"]


def test_suraggel_v13_subtipo_flag() -> None:
    sur = next(x for x in lista_racas("v13") if x["slug"] == "suraggel")
    assert sur["escolhe_suraggel_subtipo"] is True


def test_preview_tracos_anao_v13() -> None:
    p = preview_tracos_raciais("anao", regra_versao="v13")
    assert p["encontrado"] is True
    assert p["regra_versao"] == "v13"
    assert p["fortitude_bonus"] == 2
    assert p["deslocamento_m"] == 6


def test_preview_tracos_goblin_v13_furtividade() -> None:
    p = preview_tracos_raciais("goblin", regra_versao="v13")
    # v1.3: bônus de CA de tamanho não é modelado como ca_bonus racial genérico.
    assert p["ca_bonus"] == 0
    assert p["furtividade_bonus"] == 2
    assert p["tamanho"] == "pequeno"


def test_halfling_alias_hynne_v13() -> None:
    p = preview_tracos_raciais("halfling", regra_versao="v13")
    assert p["encontrado"] is True
    assert p["slug"] == "hynne"


def test_humano_versatil_pericias_extra() -> None:
    assert humano_versatil_pericias_extra("duas_pericias") == 2
    assert humano_versatil_pericias_extra("pericia_poder") == 1
    assert humano_versatil_pericias_extra(None) == 2


def test_vagas_humano_versatil_pericia_poder() -> None:
    assert (
        pericias_treinadas_extra_raca("humano", "v13", humano_versatil="pericia_poder")
        == 1
    )
    assert (
        vagas_pericias_treinadas(
            "ladino",
            0,
            "humano",
            "v13",
            humano_versatil="pericia_poder",
        )
        == 11
    )


def test_tracos_mb_legado_anao_mais4() -> None:
    row = tracos_mecanicos_por_slug("anao", "mb")
    assert row is not None
    assert row["fortitude_bonus"] == 4
