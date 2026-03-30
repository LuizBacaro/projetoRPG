from fastapi.testclient import TestClient

from app.main import app


def test_openapi_inclui_security_scheme_jwt_bearer():
    client = TestClient(app)

    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    openapi = response.json()
    schemes = openapi["components"]["securitySchemes"]
    assert "JWTBearer" in schemes
    assert schemes["JWTBearer"]["type"] == "http"
    assert schemes["JWTBearer"]["scheme"] == "bearer"
    assert schemes["JWTBearer"]["bearerFormat"] == "JWT"


def test_openapi_documenta_auth_me_com_seguranca():
    client = TestClient(app)

    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    openapi = response.json()
    operacao_me = openapi["paths"]["/api/v1/auth/me"]["get"]
    assert {"JWTBearer": []} in operacao_me["security"]


def test_openapi_login_tem_exemplo_de_resposta():
    client = TestClient(app)

    response = client.get("/api/openapi.json")

    assert response.status_code == 200
    openapi = response.json()
    operacao_login = openapi["paths"]["/api/v1/auth/login"]["post"]
    example = operacao_login["responses"]["200"]["content"]["application/json"]["example"]
    assert "access_token" in example
    assert "refresh_token" in example
    assert example["token_type"] == "bearer"