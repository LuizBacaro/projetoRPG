from types import SimpleNamespace

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd35.api.v1.combate import router as combate_router
from app.shared.core.deps import get_usuario_atual, requer_mestre_dnd35_ou_admin

_MESTRE_TESTE = SimpleNamespace(
    id=1, perfil="mestre", email="combate@test", nome="Mestre Teste"
)


class _FakeCombate:
    def __init__(self):
        self.id = 99
        self.combatentes_ids = [101, 202]
        self.turno_atual = 0
        self.rodada_atual = 1
        self.ativo = True

    def obter_combatente_ativo_id(self):
        if self.turno_atual >= len(self.combatentes_ids):
            return None
        return self.combatentes_ids[self.turno_atual]


class _FakeCondicaoService:
    def __init__(self):
        self.calls = []

    def decrementar_duracao_todas(self, combatente_id: int):
        self.calls.append(combatente_id)
        return {"combatente_id": combatente_id, "condicoes": []}


class _FakeCombateService:
    def __init__(self, combate: _FakeCombate):
        self.combate = combate
        self.received_if_match = None
        self.received_condicao_service = None
        self.received_incluir_combatentes = None

    def avancar_turno(self, if_match: str, condicao_service=None):
        self.received_if_match = if_match
        self.received_condicao_service = condicao_service

        combatente_ativo_id = self.combate.obter_combatente_ativo_id()
        if condicao_service and combatente_ativo_id is not None:
            condicao_service.decrementar_duracao_todas(combatente_ativo_id)

        self.combate.turno_atual = 1
        return self.combate

    def montar_status_combate(
        self, combate: _FakeCombate, incluir_combatentes: bool = True
    ):
        self.received_incluir_combatentes = incluir_combatentes
        payload = {
            "id": combate.id,
            "combatentes_ids": combate.combatentes_ids,
            "turno_atual": combate.turno_atual,
            "rodada_atual": combate.rodada_atual,
            "versao": "99:1:1:1",
            "ativo": combate.ativo,
            "combatente_ativo_id": combate.obter_combatente_ativo_id(),
            "resumido": not incluir_combatentes,
        }
        if incluir_combatentes:
            payload["combatentes"] = []
        return payload


def test_avancar_turno_endpoint_delega_condicoes_e_retorna_status():
    app = FastAPI()
    app.include_router(combate_router, prefix="/api/v1")

    fake_combate = _FakeCombate()
    fake_condicao_service = _FakeCondicaoService()
    fake_combate_service = _FakeCombateService(fake_combate)

    from app.core.dependencies import get_combate_service, get_condicao_service

    app.dependency_overrides[get_combate_service] = lambda: fake_combate_service
    app.dependency_overrides[get_condicao_service] = lambda: fake_condicao_service
    app.dependency_overrides[get_usuario_atual] = lambda: _MESTRE_TESTE
    app.dependency_overrides[requer_mestre_dnd35_ou_admin] = lambda: _MESTRE_TESTE

    client = TestClient(app)
    response = client.post(
        "/api/v1/combate/avancar-turno",
        headers={"If-Match": "99:1:0:1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == 99
    assert payload["turno_atual"] == 1
    assert payload["combatente_ativo_id"] == 202
    assert payload["versao"] == "99:1:1:1"
    assert payload["resumido"] is False
    assert "combatentes" in payload

    assert fake_combate_service.received_if_match == "99:1:0:1"
    assert fake_combate_service.received_incluir_combatentes is True
    assert fake_combate_service.received_condicao_service is fake_condicao_service
    assert fake_condicao_service.calls == [101]


def test_avancar_turno_endpoint_resumido_nao_retorna_combatentes():
    app = FastAPI()
    app.include_router(combate_router, prefix="/api/v1")

    fake_combate = _FakeCombate()
    fake_condicao_service = _FakeCondicaoService()
    fake_combate_service = _FakeCombateService(fake_combate)

    from app.core.dependencies import get_combate_service, get_condicao_service

    app.dependency_overrides[get_combate_service] = lambda: fake_combate_service
    app.dependency_overrides[get_condicao_service] = lambda: fake_condicao_service
    app.dependency_overrides[get_usuario_atual] = lambda: _MESTRE_TESTE
    app.dependency_overrides[requer_mestre_dnd35_ou_admin] = lambda: _MESTRE_TESTE

    client = TestClient(app)
    response = client.post(
        "/api/v1/combate/avancar-turno?resumido=true",
        headers={"If-Match": "99:1:0:1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["resumido"] is True
    assert "combatentes" not in payload
    assert fake_combate_service.received_incluir_combatentes is False
