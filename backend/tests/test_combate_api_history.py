from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd35.api.v1.combate import router as combate_router


class _FakeCombateService:
    def listar_historico(self, skip: int = 0, limit: int = 20):
        return {
            "total": 1,
            "skip": skip,
            "limit": limit,
            "itens": [
                {
                    "id": 10,
                    "combate_id": 2,
                    "combatentes_ids": [1, 2],
                    "total_combatentes": 2,
                    "total_vivos": 1,
                    "total_rodadas": 3,
                    "total_turnos": 6,
                    "vencedor_id": 1,
                    "vencedor_nome": "Theron",
                    "vencedor_tipo": "jogador",
                    "motivo_encerramento": "manual",
                    "estatisticas": {"vivos": 1, "mortos": 1, "hp_total_restante": 12, "combatentes": []},
                    "finalizado_em": "2026-03-29T12:00:00",
                }
            ],
        }


def test_listar_historico_endpoint_retorna_payload_paginado():
    app = FastAPI()
    app.include_router(combate_router, prefix="/api/v1")

    fake_service = _FakeCombateService()

    from app.core.dependencies import get_combate_service
    from app.shared.core.deps import get_usuario_atual

    app.dependency_overrides[get_combate_service] = lambda: fake_service
    app.dependency_overrides[get_usuario_atual] = lambda: object()

    client = TestClient(app)
    response = client.get("/api/v1/combate/historico?skip=5&limit=15")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["skip"] == 5
    assert payload["limit"] == 15
    assert payload["itens"][0]["motivo_encerramento"] == "manual"
