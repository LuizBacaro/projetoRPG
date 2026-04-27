from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd35.api.v1.tabelas_classes import router as tabelas_classes_router
from app.shared.core.catalog_cache import catalog_cache
from app.shared.core.config import settings
from app.shared.core.deps import get_usuario_atual
from app.games.dnd35.services.tabelas_classes_service import TabelasClassesService


def _build_client() -> TestClient:
    app = FastAPI()
    app.include_router(tabelas_classes_router, prefix="/api/v1")
    app.dependency_overrides[get_usuario_atual] = lambda: object()
    return TestClient(app)


def _set_feature_flag(value: bool) -> bool:
    original = settings.CLASSES_TABLES_CATALOG_ENABLED
    settings.CLASSES_TABLES_CATALOG_ENABLED = value
    return original


def _restore_feature_flag(original: bool) -> None:
    settings.CLASSES_TABLES_CATALOG_ENABLED = original


def test_tabelas_classes_retorna_404_quando_feature_flag_desligada():
    client = _build_client()
    original = _set_feature_flag(False)
    try:
        response = client.get("/api/v1/tabelas-classes/")
    finally:
        _restore_feature_flag(original)

    assert response.status_code == 404
    assert response.json()["detail"] == "Recurso não habilitado"


def test_tabelas_classes_lista_suporta_paginacao_e_filtro(monkeypatch):
    payload = {
        "total": 1,
        "skip": 0,
        "limit": 10,
        "items": [
            {
                "table_number": 18,
                "title": "Tabela 3-18: Inimigos Prediletos do Ranger",
                "source_file": "Tabela_3-18_Inimigos_Prediletos_do_Ranger.xlsx",
                "metadata": {"Tabela": "3-18"},
                "header": ["Tipo", "Exemplos"],
                "rows": [{"Tipo": "Aberração", "Exemplos": "Beholders"}],
            }
        ],
    }

    def _fake_listar(self, skip=0, limit=100, table_number=None):
        assert skip == 0
        assert limit == 10
        assert table_number == 18
        return payload

    monkeypatch.setattr(TabelasClassesService, "listar_tabelas", _fake_listar)
    client = _build_client()
    original = _set_feature_flag(True)
    try:
        response = client.get("/api/v1/tabelas-classes/", params={"skip": 0, "limit": 10, "table_number": 18})
    finally:
        _restore_feature_flag(original)
        catalog_cache.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert body["items"][0]["table_number"] == 18


def test_tabelas_classes_lista_usa_cache_em_requisicoes_iguais(monkeypatch):
    called = {"listar": 0}

    def _fake_listar(self, skip=0, limit=100, table_number=None):
        called["listar"] += 1
        return {
            "total": 1,
            "skip": skip,
            "limit": limit,
            "items": [
                {
                    "table_number": 3,
                    "title": "Tabela 3-3: O Bárbaro",
                    "source_file": "Tabela_3-3_O_Bárbaro.xlsx",
                    "metadata": {"Tabela": "3-3"},
                    "header": ["col_1"],
                    "rows": [{"col_1": "1°"}],
                }
            ],
        }

    monkeypatch.setattr(TabelasClassesService, "listar_tabelas", _fake_listar)
    original_cache_enabled = settings.CACHE_ENABLED
    original_flag = _set_feature_flag(True)
    settings.CACHE_ENABLED = True
    catalog_cache.clear()
    client = _build_client()

    try:
        r1 = client.get("/api/v1/tabelas-classes/", params={"skip": 0, "limit": 10})
        r2 = client.get("/api/v1/tabelas-classes/", params={"skip": 0, "limit": 10})
    finally:
        settings.CACHE_ENABLED = original_cache_enabled
        _restore_feature_flag(original_flag)
        catalog_cache.clear()

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert called["listar"] == 1


def test_tabela_classes_detail_usa_cache_em_requisicoes_iguais(monkeypatch):
    called = {"obter": 0}

    def _fake_obter(self, table_number):
        called["obter"] += 1
        return {
            "table_number": table_number,
            "title": "Tabela fake",
            "source_file": "fake.xlsx",
            "metadata": {"Tabela": "3-9"},
            "header": ["col_1"],
            "rows": [{"col_1": "foo"}],
        }

    monkeypatch.setattr(TabelasClassesService, "obter_tabela", _fake_obter)
    original_cache_enabled = settings.CACHE_ENABLED
    original_flag = _set_feature_flag(True)
    settings.CACHE_ENABLED = True
    catalog_cache.clear()
    client = _build_client()

    try:
        r1 = client.get("/api/v1/tabelas-classes/9")
        r2 = client.get("/api/v1/tabelas-classes/9")
    finally:
        settings.CACHE_ENABLED = original_cache_enabled
        _restore_feature_flag(original_flag)
        catalog_cache.clear()

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert called["obter"] == 1
