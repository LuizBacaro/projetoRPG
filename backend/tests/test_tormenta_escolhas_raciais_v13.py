"""Escolhas raciais v1.3 — Lefou, Qareen, Dahllan (RF-T02-v13)."""

from __future__ import annotations

from app.games.tormenta.rules.escolhas_raciais_t20 import (
    aplicar_escolhas_ao_preview,
    escolhas_por_raca,
    magias_inatas_raca_v13,
    validar_escolhas_raciais_v13,
)
from app.games.tormenta.rules.racas_t20 import lista_racas
from app.games.tormenta.rules.tracos_raciais_t20 import preview_tracos_raciais


def test_escolhas_lefou_catalogo() -> None:
    cfg = escolhas_por_raca("lefou", "v13")
    assert cfg is not None
    assert cfg["tipo"] == "deformidade"
    assert len(cfg.get("modos") or []) == 2


def test_escolhas_qareen_ascendencias() -> None:
    cfg = escolhas_por_raca("qareen", "v13")
    assert cfg is not None
    slugs = {a["slug"] for a in cfg.get("ascendencias") or []}
    assert slugs == {"agua", "ar", "fogo", "terra", "luz", "trevas"}


def test_preview_lefou_deformidade_pericias() -> None:
    p = preview_tracos_raciais(
        "lefou",
        regra_versao="v13",
        lefou_deformidade_modo="duas_pericias",
        lefou_deformidade_pericias=["Acrobacia", "Intimidação"],
    )
    assert p["pericias_bonus"]["Acrobacia"] == 2
    assert p["pericias_bonus"]["Intimidação"] == 2


def test_preview_qareen_rd_fogo() -> None:
    p = preview_tracos_raciais(
        "qareen",
        regra_versao="v13",
        qareen_ascendencia="fogo",
    )
    assert p["reducao_dano"].get("fogo") == 10


def test_preview_dahllan_magias_inatas() -> None:
    p = preview_tracos_raciais("dahllan", regra_versao="v13")
    assert "controlar_plantas" in p["magias_inatas"]
    assert magias_inatas_raca_v13("dahllan") == ["controlar_plantas"]


def test_preview_elfo_deslocamento_12() -> None:
    p = preview_tracos_raciais("elfo", regra_versao="v13")
    assert p["deslocamento_m"] == 12
    assert p["tamanho_ui"] == "M"


def test_preview_anao_desloc_nao_reduz() -> None:
    p = preview_tracos_raciais("anao", regra_versao="v13")
    assert p["deslocamento_m"] == 6
    assert p["desloc_nao_reduz_armadura_carga"] is True


def test_preview_sereia_natacao() -> None:
    p = preview_tracos_raciais("sereia_tritao", regra_versao="v13")
    assert p["deslocamento_natacao_m"] == 12


def test_preview_silfide_minusculo_voo() -> None:
    p = preview_tracos_raciais("silfide", regra_versao="v13")
    assert p["tamanho"] == "minusculo"
    assert p["tamanho_ui"] == "Min"
    assert p["deslocamento_voo_m"] == 12


def test_validar_lefou_duas_pericias() -> None:
    ok, erros = validar_escolhas_raciais_v13(
        "lefou",
        lefou_deformidade_modo="duas_pericias",
        lefou_deformidade_pericias=["Acrobacia"],
    )
    assert ok is False
    assert erros


def test_validar_qareen_completo() -> None:
    ok, erros = validar_escolhas_raciais_v13(
        "qareen",
        qareen_ascendencia="agua",
        qareen_magia_slug="escudo",
    )
    assert ok is True
    assert not erros


def test_lista_racas_flags_escolhas() -> None:
    lef = next(x for x in lista_racas("v13") if x["slug"] == "lefou")
    qar = next(x for x in lista_racas("v13") if x["slug"] == "qareen")
    dah = next(x for x in lista_racas("v13") if x["slug"] == "dahllan")
    assert lef["escolhe_lefou_deformidade"] is True
    assert qar["escolhe_qareen_ascendencia"] is True
    assert dah["magias_inatas_v13"] is True


def test_preview_osteon_memoria_pericia() -> None:
    p = preview_tracos_raciais(
        "osteon",
        regra_versao="v13",
        osteon_memoria_modo="pericia",
        osteon_memoria_pericia="Sobrevivência",
    )
    assert "Sobrevivência" in (p.get("pericias_treinadas_escolha") or [])


def test_preview_sereia_magias() -> None:
    p = preview_tracos_raciais(
        "sereia_tritao",
        regra_versao="v13",
        sereia_magias=["hipnotismo", "sono"],
    )
    assert "hipnotismo" in p["magias_inatas"]
    assert "sono" in p["magias_inatas"]


def test_validar_sereia_duas_magias() -> None:
    ok, erros = validar_escolhas_raciais_v13(
        "sereia_tritao",
        sereia_magias=["hipnotismo"],
    )
    assert ok is False
    ok2, _ = validar_escolhas_raciais_v13(
        "sereia_tritao",
        sereia_magias=["hipnotismo", "sono"],
    )
    assert ok2 is True


def test_lista_racas_flags_osteon_sereia() -> None:
    ost = next(x for x in lista_racas("v13") if x["slug"] == "osteon")
    ser = next(x for x in lista_racas("v13") if x["slug"] == "sereia_tritao")
    assert ost["escolhe_osteon_memoria"] is True
    assert ser["escolhe_sereia_magias"] is True


def test_preview_golem_fonte_elemental() -> None:
    p = preview_tracos_raciais(
        "golem",
        regra_versao="v13",
        golem_fonte_elemental="fogo",
    )
    assert p["imunidades_dano"].get("fogo") is True
    assert p["deslocamento_m"] == 6
    assert p["ca_bonus"] == 2


def test_validar_golem_completo() -> None:
    ok, erros = validar_escolhas_raciais_v13("golem", golem_fonte_elemental="agua")
    assert ok is False
    ok2, _ = validar_escolhas_raciais_v13(
        "golem",
        golem_fonte_elemental="agua",
        golem_poder_geral_slug="ataque_poderoso",
    )
    assert ok2 is True


def test_preview_kliren_hibrido_vanguardista() -> None:
    p = preview_tracos_raciais(
        "kliren",
        regra_versao="v13",
        kliren_pericia="Conhecimento",
        kliren_oficio="alquimia",
    )
    assert "Conhecimento" in (p.get("pericias_treinadas_escolha") or [])
    assert p["pericias_bonus"].get("Ofício") == 2


def test_preview_silfide_magias() -> None:
    p = preview_tracos_raciais(
        "silfide",
        regra_versao="v13",
        silfide_magias=["luz", "sono"],
    )
    assert "luz" in p["magias_inatas"]
    assert p["tamanho"] == "minusculo"


def test_lista_racas_flags_golem_kliren_silfide() -> None:
    gol = next(x for x in lista_racas("v13") if x["slug"] == "golem")
    kli = next(x for x in lista_racas("v13") if x["slug"] == "kliren")
    sil = next(x for x in lista_racas("v13") if x["slug"] == "silfide")
    assert gol["escolhe_golem_fonte"] is True
    assert kli["escolhe_kliren_hibrido"] is True
    assert sil["escolhe_silfide_magias"] is True


def test_aplicar_escolhas_merge_pericias() -> None:
    base = {
        "pericias_bonus": {"Adestramento": 2},
        "reducao_dano": {},
        "magias_inatas": [],
        "escolhas_resumo": [],
    }
    out = aplicar_escolhas_ao_preview(
        base,
        "lefou",
        regra_versao="v13",
        lefou_deformidade_pericias=["Acrobacia"],
    )
    assert out["pericias_bonus"]["Adestramento"] == 2
    assert out["pericias_bonus"]["Acrobacia"] == 2
