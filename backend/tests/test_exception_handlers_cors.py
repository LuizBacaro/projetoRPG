"""Garante que erros de banco voltam como JSON com CORS habilitado.

Regressão para o sintoma "Failed to fetch" em produção: quando uma exceção
(IntegrityError / OperationalError / Exception) escapa para o Starlette,
algumas configurações de proxy (Render) entregam ao navegador uma resposta
sem `Access-Control-Allow-Origin`, e o frontend só vê `TypeError: Failed to
fetch`. Os handlers globais cobrem isso retornando JSON 4xx/5xx que passa
pelo CORSMiddleware.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, OperationalError

from app.shared.core.config import settings


@pytest.fixture(scope="module")
def client():
    from app.main import app

    @app.get("/__test__/integrity-error")
    def _trigger_integrity():  # pragma: no cover - exec via TestClient
        raise IntegrityError(
            "UPDATE...", {}, Exception("CHECK constraint failed: ck_combatentes_hp_atual_non_negative")
        )

    @app.get("/__test__/operational-error")
    def _trigger_operational():  # pragma: no cover
        raise OperationalError("SELECT 1", {}, Exception("connection refused"))

    @app.get("/__test__/uncaught-error")
    def _trigger_uncaught():  # pragma: no cover
        raise RuntimeError("boom")

    return TestClient(app, raise_server_exceptions=False)


def _origem_permitida() -> str:
    """Usa a primeira origem do CORS configurada para o ambiente de teste."""
    for raw in settings.ALLOWED_ORIGINS:
        if raw and raw != "*":
            return raw
    return "*"


def _expect_cors(response, status_esperado: int):
    assert response.status_code == status_esperado, response.text
    assert response.headers.get("content-type", "").startswith("application/json")
    headers_lower = {k.lower(): v for k, v in response.headers.items()}
    assert "access-control-allow-origin" in headers_lower, (
        "Resposta de erro DEVE preservar CORS — sem isto o browser mostra apenas "
        "'Failed to fetch'. Headers recebidos: " + str(headers_lower)
    )
    assert "detail" in response.json()


def test_integrity_error_responde_409_com_cors(client):
    resp = client.get(
        "/__test__/integrity-error",
        headers={"Origin": _origem_permitida()},
    )
    _expect_cors(resp, 409)
    detail = resp.json()["detail"].lower()
    assert "regra antiga" in detail or "integridade" in detail


def test_operational_error_responde_503_com_cors(client):
    resp = client.get(
        "/__test__/operational-error",
        headers={"Origin": _origem_permitida()},
    )
    _expect_cors(resp, 503)


def test_excecao_generica_responde_500_com_cors(client):
    resp = client.get(
        "/__test__/uncaught-error",
        headers={"Origin": _origem_permitida()},
    )
    _expect_cors(resp, 500)
