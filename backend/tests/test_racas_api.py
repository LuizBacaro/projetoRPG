from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.racas import router as racas_router


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(racas_router, prefix="/api/v1")
    return TestClient(app)


def test_listar_racas_retorna_catalogo():
    client = _client()
    response = client.get("/api/v1/racas")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert any(item.get("slug") == "elfos" for item in body)


def test_obter_raca_por_slug():
    client = _client()
    response = client.get("/api/v1/racas/elfos")
    assert response.status_code == 200
    body = response.json()
    assert body["nome"] == "Elfos"
    assert isinstance(body["modificadores_habilidade"], list)
