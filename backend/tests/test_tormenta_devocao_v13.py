"""Devoção v1.3 — validação de divindade e poder concedido."""

from __future__ import annotations

import pytest

from app.games.tormenta.rules.tendencias_divindades_t20 import (
    divindade_por_slug,
    validar_devocao_v13,
)
from app.games.tormenta.services.personagem_service import TormentaPersonagemService
from app.shared.exceptions.custom_exceptions import DadosInvalidos


def test_divindade_por_slug_khalmyr():
    row = divindade_por_slug("khalmyr")
    assert row is not None
    assert row.get("poderes_concedidos")


def test_validar_devocao_v13_sem_devoto_ok():
    ok, msg = validar_devocao_v13({"regra_versao": "v13"})
    assert ok is True
    assert msg == ""


def test_validar_devocao_v13_devoto_sem_divindade_rejeita():
    ok, msg = validar_devocao_v13({"regra_versao": "v13", "devoto": True})
    assert ok is False
    assert "divindade" in msg.lower()


def test_validar_devocao_v13_devoto_com_poder_ok():
    row = divindade_por_slug("khalmyr")
    assert row
    pod = row["poderes_concedidos"][0]
    ok, msg = validar_devocao_v13(
        {
            "regra_versao": "v13",
            "devoto": True,
            "tormenta_divindade_mb_slug": "khalmyr",
            "poder_concedido_slug": pod,
        }
    )
    assert ok is True
    assert msg == ""


def test_validar_devocao_v13_poder_invalido_rejeita():
    ok, msg = validar_devocao_v13(
        {
            "regra_versao": "v13",
            "tormenta_divindade_mb_slug": "khalmyr",
            "poder_concedido_slug": "poder_inexistente_xyz",
        }
    )
    assert ok is False
    assert "invalido" in msg.lower()


def test_service_validar_devocao_v13() -> None:
    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    row = divindade_por_slug("khalmyr")
    assert row
    svc._validar_devocao_v13(
        "jogador",
        {
            "regra_versao": "v13",
            "devoto": True,
            "tormenta_divindade_mb_slug": "khalmyr",
            "poder_concedido_slug": row["poderes_concedidos"][0],
        },
    )


def test_service_devoto_sem_poder_rejeita() -> None:
    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    with pytest.raises(DadosInvalidos, match="poder concedido"):
        svc._validar_devocao_v13(
            "jogador",
            {
                "regra_versao": "v13",
                "devoto": True,
                "tormenta_divindade_mb_slug": "khalmyr",
            },
        )
