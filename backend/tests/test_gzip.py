from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.testclient import TestClient


def _build_gzip_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(GZipMiddleware, minimum_size=100)

    @app.get("/payload")
    async def payload():
        return {"conteudo": "x" * 2048}

    return app


def test_gzip_comprime_resposta_json_grande():
    client = TestClient(_build_gzip_app())

    response = client.get("/payload", headers={"Accept-Encoding": "gzip"})

    assert response.status_code == 200
    assert response.headers.get("content-encoding") == "gzip"