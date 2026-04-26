from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.v1.magias import router as magias_router
from app.core.database import Base, get_db
from app.core.deps import get_usuario_atual, requer_mestre_ou_admin
from app.games.dnd35.services.magia_import_service import MagiaImportService


@pytest.fixture(scope="function")
def import_db():
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
    app.dependency_overrides[get_usuario_atual] = lambda: object()
    app.dependency_overrides[requer_mestre_ou_admin] = lambda: object()

    return TestClient(app)


def test_preview_importacao_valida_e_confirma_importa_linhas(import_db, monkeypatch):
    _, db_factory = import_db
    client = _build_client(db_factory)

    def _fake_loader(self, _filename, _content):
        return [
            (
                2,
                {
                    "nome": "Armadura Arcana",
                    "nome_en": "Mage Armor",
                    "escola": "Abjuracao",
                    "sub_escola": "",
                    "descritor": "",
                    "classes_niveis": "MAGO:1;BARDO:1",
                    "componentes": "V,G,F",
                    "componente_extra": "",
                    "tempo_conjuracao": "1 acao",
                    "alcance": "toque",
                    "area_efeito": "criatura tocada",
                    "duracao": "1 hora",
                    "teste_resistencia": "Nenhum",
                    "resistencia_magica": "nao",
                    "resistencia_magia_texto": "",
                    "dano": "",
                    "descricao": "Campo de forca invisivel protege o alvo.",
                    "descricao_en": "",
                    "e_magia_dominio": "nao",
                    "dominios": "",
                    "pagina_referencia": "249",
                },
            )
        ]

    monkeypatch.setattr(MagiaImportService, "_carregar_linhas_excel", _fake_loader)

    preview = client.post(
        "/api/v1/magias/importacao/preview",
        files={"arquivo": ("magias.xlsx", b"dummy", "application/octet-stream")},
    )

    assert preview.status_code == 200
    body = preview.json()
    assert body["validas"] == 1
    assert body["invalidas"] == 0
    assert body["preview"][0]["nome"] == "Armadura Arcana"

    confirmar = client.post(
        "/api/v1/magias/importacao/confirmar",
        json={"import_id": body["import_id"]},
    )

    assert confirmar.status_code == 200
    result = confirmar.json()
    assert result["importadas"] == 1
    assert result["falhas"] == 0

    listar = client.get("/api/v1/magias/?nome=Armadura")
    assert listar.status_code == 200
    assert len(listar.json()) == 1


def test_preview_importacao_rejeita_extensao_invalida(import_db):
    _, db_factory = import_db
    client = _build_client(db_factory)

    preview = client.post(
        "/api/v1/magias/importacao/preview",
        files={"arquivo": ("magias.csv", b"dummy", "text/csv")},
    )

    assert preview.status_code == 422
    assert "Formato de arquivo não suportado" in preview.json()["detail"]
