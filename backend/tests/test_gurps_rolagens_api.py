"""Integração HTTP — rolagens GURPS (3d6)."""

from __future__ import annotations

from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.gurps.api.v1.rolagens import router as gurps_rolagens_router
from app.shared.core.deps import get_usuario_atual
def _usuario_stub() -> SimpleNamespace:
    return SimpleNamespace(id=1, perfil="jogador", email="u@x", nome="U")


def _build_client() -> TestClient:
    app = FastAPI()
    app.include_router(gurps_rolagens_router, prefix="/api/v1")
    app.dependency_overrides[get_usuario_atual] = _usuario_stub
    return TestClient(app)


def test_rolagem_3d6_com_dados_informados_sucesso_decisivo():
    client = _build_client()
    r = client.post("/api/v1/gurps/rolagens/3d6", json={"nivel_efetivo": 12, "dados": [1, 1, 1]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 3
    assert body["sucesso"] is True
    assert body["margem"] == 9
    assert body["sucesso_decisivo"] is True
    assert body["falha_critica"] is False


def test_rolagem_3d6_com_dados_informados_falha_critica():
    client = _build_client()
    r = client.post("/api/v1/gurps/rolagens/3d6", json={"nivel_efetivo": 12, "dados": [6, 6, 6]})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["total"] == 18
    assert body["sucesso"] is False
    assert body["margem"] == 6
    assert body["falha_critica"] is True


def test_rolagem_3d6_rejeita_dados_invalidos():
    client = _build_client()
    r = client.post("/api/v1/gurps/rolagens/3d6", json={"nivel_efetivo": 12, "dados": [0, 7, 1]})
    assert r.status_code == 422
    assert "3 valores entre 1 e 6" in str(r.json().get("detail", ""))


def test_calcula_nivel_efetivo_com_modificadores():
    client = _build_client()
    r = client.post(
        "/api/v1/gurps/rolagens/nivel-efetivo",
        json={"nh_base": 12, "modificadores": [1, -2, 3]},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["nh_base"] == 12
    assert body["soma_modificadores"] == 2
    assert body["nivel_efetivo"] == 14


def test_calcula_nivel_efetivo_sem_modificadores():
    client = _build_client()
    r = client.post("/api/v1/gurps/rolagens/nivel-efetivo", json={"nh_base": 11})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["soma_modificadores"] == 0
    assert body["nivel_efetivo"] == 11


def test_rolagem_dano_por_expressao_valida():
    client = _build_client()
    r = client.post("/api/v1/gurps/rolagens/dano", json={"expressao": "2d+1"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["expressao"] == "2d+1"
    assert len(body["dados_rolados"]) == 2
    assert body["modificador"] == 1
    assert body["total"] == body["total_sem_modificador"] + 1


def test_rolagem_dano_rejeita_expressao_invalida():
    client = _build_client()
    r = client.post("/api/v1/gurps/rolagens/dano", json={"expressao": "abc"})
    assert r.status_code == 422
    assert "Nd" in str(r.json().get("detail", ""))

