"""Origens Heróis de Arton — troca de perícia redundante (RF-HA03d)."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.origens_t20 import (
    aplicar_pericias_origem_em_lista,
    contar_vagas_pericias_extra_origem_resolvidas,
    resolver_pericias_origem_efetivas,
    sincronizar_pericias_origem_ficha_json,
    validar_trocas_pericia_origem,
)
from app.games.tormenta.rules.pericias_classe_t20 import slugs_pericias_treinadas
from app.games.tormenta.rules.pericias_criacao_t20 import validar_pericias_ficha


def _pericias_nobre_com_diplomacia() -> list[dict]:
    """Nobre 1º: vontade + diplomacia (ou) + 4 escolhas."""
    return [
        {"nome": "Vontade", "treinado": True},
        {"nome": "Diplomacia", "treinado": True},
        {"nome": "Guerra", "treinado": True},
        {"nome": "Nobreza", "treinado": True},
        {"nome": "Percepção", "treinado": True},
        {"nome": "Atletismo", "treinado": True},
    ]


def test_resolver_pericia_redundante_com_troca() -> None:
    per = _pericias_nobre_com_diplomacia()
    treinados = slugs_pericias_treinadas(per, "v13")
    efetivas, meta = resolver_pericias_origem_efetivas(
        "bacharel",
        ["pericia:diplomacia", "poder:retórica"],
        treinados,
        "nobre",
        {"diplomacia": "iniciativa"},
    )
    assert efetivas == ["iniciativa"]
    assert meta["redundantes"] == ["diplomacia"]
    assert meta["trocas_aplicadas"] == {"diplomacia": "iniciativa"}


def test_redundante_sem_troca_nao_gasta_vaga_extra() -> None:
    per = _pericias_nobre_com_diplomacia()
    treinados = slugs_pericias_treinadas(per, "v13")
    assert (
        contar_vagas_pericias_extra_origem_resolvidas(
            "bacharel",
            ["pericia:diplomacia", "poder:retórica"],
            treinados,
            "nobre",
            None,
        )
        == 0
    )


def test_aplicar_origem_com_troca_marca_substituta() -> None:
    per = aplicar_pericias_origem_em_lista(
        _pericias_nobre_com_diplomacia(),
        ["pericia:diplomacia", "poder:retórica"],
        regra_versao="v13",
        slug_origem="bacharel",
        slug_classe="nobre",
        origem_trocas={"diplomacia": "iniciativa"},
    )
    slugs = slugs_pericias_treinadas(per, "v13")
    assert "diplomacia" in slugs
    assert "iniciativa" in slugs


def test_sincronizar_ficha_json_com_troca() -> None:
    fj = sincronizar_pericias_origem_ficha_json(
        {
            "regra_versao": "v13",
            "tormenta_classe_mb_slug": "nobre",
            "origem_slug": "bacharel",
            "origem_beneficios": ["pericia:diplomacia", "poder:retórica"],
            "origem_trocas_pericia": {"diplomacia": "iniciativa"},
            "pericias": _pericias_nobre_com_diplomacia(),
        }
    )
    slugs = slugs_pericias_treinadas(fj["pericias"], "v13")
    assert "iniciativa" in slugs


def test_validar_pericias_nobre_bacharel_com_troca() -> None:
    ok, _, res = validar_pericias_ficha(
        nivel=1,
        slug_classe="nobre",
        int_valor=0,
        slug_raca=None,
        pericias=_pericias_nobre_com_diplomacia(),
        regra_versao="v13",
        origem_beneficios=["pericia:diplomacia", "poder:retórica"],
        origem_slug="bacharel",
        origem_trocas_pericia={"diplomacia": "iniciativa"},
    )
    assert ok is True
    assert res["pericias_treinadas_extra_origem"] == 1
    assert res["vagas_treinadas"] == 7
    assert res["origem_pericias"]["efetivas"] == ["iniciativa"]


def test_validar_troca_rejeita_forasteira() -> None:
    ok, msg = validar_trocas_pericia_origem(
        "bacharel",
        ["pericia:diplomacia", "poder:retórica"],
        {"diplomacia": "adestramento"},
        "nobre",
        _pericias_nobre_com_diplomacia(),
    )
    assert ok is False
    assert "classe" in msg.lower()


def test_validar_troca_rejeita_quando_nao_redundante() -> None:
    per = [
        {"nome": "Vontade", "treinado": True},
        {"nome": "Intimidação", "treinado": True},
        {"nome": "Guerra", "treinado": True},
        {"nome": "Nobreza", "treinado": True},
        {"nome": "Percepção", "treinado": True},
        {"nome": "Atletismo", "treinado": True},
    ]
    ok, msg = validar_trocas_pericia_origem(
        "bacharel",
        ["pericia:conhecimento", "poder:retórica"],
        {"conhecimento": "guerra"},
        "nobre",
        per,
    )
    assert ok is False
    assert "treinada" in msg.lower()


def test_origem_sem_flag_troca_rejeita_mapa() -> None:
    ok, msg = validar_trocas_pericia_origem(
        "cao_de_briga",
        ["pericia:oficio", "poder:rd_corte_2"],
        {"oficio": "luta"},
        "barbaro",
        [{"nome": "Luta", "treinado": True}],
    )
    assert ok is False
    assert "não permite" in msg.lower()


def test_validar_origem_v13_com_troca_no_service() -> None:
    from app.games.tormenta.services.personagem_service import TormentaPersonagemService

    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    svc._validar_origem_v13(
        "jogador",
        {
            "regra_versao": "v13",
            "origem_slug": "bacharel",
            "tormenta_classe_mb_slug": "nobre",
            "origem_beneficios": ["pericia:diplomacia", "poder:retórica"],
            "origem_trocas_pericia": {"diplomacia": "iniciativa"},
            "pericias": _pericias_nobre_com_diplomacia(),
        },
        criacao=True,
    )


def test_validar_origem_v13_troca_invalida_levanta() -> None:
    from app.games.tormenta.services.personagem_service import TormentaPersonagemService
    from app.shared.exceptions.custom_exceptions import DadosInvalidos

    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    with pytest.raises(DadosInvalidos, match="treinada"):
        svc._validar_origem_v13(
            "jogador",
            {
                "regra_versao": "v13",
                "origem_slug": "bacharel",
                "tormenta_classe_mb_slug": "nobre",
                "origem_beneficios": ["pericia:conhecimento", "poder:retórica"],
                "origem_trocas_pericia": {"conhecimento": "guerra"},
                "pericias": _pericias_nobre_com_diplomacia(),
            },
            criacao=True,
        )
