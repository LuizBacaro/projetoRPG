"""Arcanista v1.3 — caminho obrigatório na criação."""

from __future__ import annotations

import pytest

from app.games.tormenta.services.personagem_service import TormentaPersonagemService
from app.shared.exceptions.custom_exceptions import DadosInvalidos


def test_arcanista_sem_caminho_rejeita() -> None:
    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    with pytest.raises(DadosInvalidos, match="caminho"):
        svc._validar_arcanista_caminho_v13(
            "jogador",
            {
                "regra_versao": "v13",
                "tormenta_classe_mb_slug": "arcanista",
            },
        )


def test_arcanista_com_mago_ok() -> None:
    svc = TormentaPersonagemService(None)  # type: ignore[arg-type]
    svc._validar_arcanista_caminho_v13(
        "jogador",
        {
            "regra_versao": "v13",
            "tormenta_classe_mb_slug": "arcanista",
            "arcanista_caminho": "mago",
        },
    )
