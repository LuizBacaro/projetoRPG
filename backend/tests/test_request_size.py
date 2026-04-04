from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.request_size import RequestSizeLimitMiddleware


def _build_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(
        RequestSizeLimitMiddleware,
        max_request_size=256,
        max_json_body_size=64,
    )

    @app.post("/echo")
    async def echo(payload: dict):
        return payload

    return app


def test_request_size_middleware_aceita_payload_pequeno():
    client = TestClient(_build_app())

    response = client.post("/echo", json={"texto": "ok"})

    assert response.status_code == 200
    assert response.json() == {"texto": "ok"}


def test_request_size_middleware_bloqueia_json_grande():
    client = TestClient(_build_app())

    response = client.post("/echo", json={"texto": "x" * 200})

    assert response.status_code == 413
    assert response.json()["detail"] == "Payload maior que o limite permitido"