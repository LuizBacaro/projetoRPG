from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.games.dnd35.api.v1.magias import router as magias_router
from app.core.database import Base, get_db
from app.shared.core.deps import get_usuario_atual, requer_mestre_ou_admin


class _UsuarioDummy:
    def __init__(self, user_id: int = 77):
        self.id = user_id


@pytest.fixture(scope="function")
def magias_hist_db():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    db = testing_session_local()
    try:
        yield db, testing_session_local
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


def _build_client(test_db_factory):
    app = FastAPI()
    app.include_router(magias_router, prefix="/api/v1")

    def _override_get_db():
        db = test_db_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _override_get_db
    app.dependency_overrides[get_usuario_atual] = lambda: _UsuarioDummy(77)
    app.dependency_overrides[requer_mestre_ou_admin] = lambda: _UsuarioDummy(77)

    return TestClient(app)


def _payload(nome: str):
    return {
        "nome": nome,
        "escola": "Evocacao",
        "componentes": "V,G",
        "alcance": "medio",
        "duracao": "instantanea",
        "tempo_conjuracao": "1 acao",
        "descricao": "Descricao de teste",
        "classes_niveis": [{"classe": "MAGO", "nivel": 1}],
    }


def test_historico_registra_criacao_e_edicao(magias_hist_db):
    _, db_factory = magias_hist_db
    client = _build_client(db_factory)

    criar = client.post("/api/v1/magias", json=_payload("Raio Historico"))
    assert criar.status_code == 201
    magia_id = criar.json()["id"]

    atualizar = client.put(
        f"/api/v1/magias/{magia_id}",
        json={"descricao": "Descricao alterada para auditoria"},
    )
    assert atualizar.status_code == 200

    historico = client.get(f"/api/v1/magias/{magia_id}/historico")
    assert historico.status_code == 200
    body = historico.json()
    assert len(body) >= 2
    assert body[0]["acao"] == "EDICAO"
    assert body[1]["acao"] == "CRIACAO"
    assert body[0]["usuario_id"] == 77


def test_historico_registra_desativacao(magias_hist_db):
    _, db_factory = magias_hist_db
    client = _build_client(db_factory)

    criar = client.post("/api/v1/magias", json=_payload("Toque de Auditoria"))
    assert criar.status_code == 201
    magia_id = criar.json()["id"]

    desativar = client.patch(f"/api/v1/magias/{magia_id}/desativar")
    assert desativar.status_code == 200

    historico = client.get(f"/api/v1/magias/{magia_id}/historico?limit=5")
    assert historico.status_code == 200
    body = historico.json()
    assert any(item["acao"] == "DESATIVACAO" for item in body)
