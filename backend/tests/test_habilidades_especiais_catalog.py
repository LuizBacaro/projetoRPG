"""
Testes do pipeline e API do catálogo de Habilidades Especiais.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.games.dnd35.api.v1.habilidades_especiais import router as habilidades_router
from app.core.habilidades_especiais_catalog import (
    get_habilidade_by_slug,
    list_habilidades,
    resolver_por_texto,
)


_REPO_ROOT = Path(__file__).resolve().parents[2]
PLANILHA_V2 = _REPO_ROOT / "Características especiais_v2.xlsx"


def _load_from_path(alias: str, relative_path: str) -> ModuleType:
    abs_path = _REPO_ROOT / relative_path
    spec = importlib.util.spec_from_file_location(alias, abs_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[alias] = module
    spec.loader.exec_module(module)
    return module


_pipeline_mod = _load_from_path(
    "_habilidades_especiais_catalog_pipeline",
    "scripts/habilidades_especiais_catalog_pipeline.py",
)

HabilidadesCatalogPipeline = _pipeline_mod.HabilidadesCatalogPipeline
HabilidadesNormalizer = _pipeline_mod.HabilidadesNormalizer
HabilidadesWorkbookReader = _pipeline_mod.HabilidadesWorkbookReader
slug_habilidade = _pipeline_mod.slug_habilidade


# ─── Pipeline ────────────────────────────────────────────────────────────


def test_slug_habilidade_normaliza_acentos_e_espacos():
    assert slug_habilidade("Fúria") == "furia"
    assert slug_habilidade("Música de bardo: fascinar") == "musica-de-bardo-fascinar"


def test_normalizer_dedupa_por_slug():
    rows = [
        {"titulo": "Fúria", "descricao": "a"},
        {"titulo": "Furia", "descricao": "b"},  # mesmo slug
    ]
    result = HabilidadesNormalizer().normalize(rows)
    slugs = [h["slug"] for h in result.habilidades]
    assert slugs == ["furia"]
    assert any(w.campo == "slug" and "duplicado" in w.mensagem for w in result.warnings)


@pytest.mark.skipif(not PLANILHA_V2.exists(), reason="planilha v2 ausente")
def test_pipeline_gera_catalogo_da_planilha_v2():
    pipeline = HabilidadesCatalogPipeline(
        reader=HabilidadesWorkbookReader(PLANILHA_V2),
        normalizer=HabilidadesNormalizer(),
    )
    result = pipeline.run()

    slugs = {h["slug"] for h in result.habilidades}
    esperados = {"furia", "esquiva-sobrenatural", "visao-no-escuro", "visao-na-penumbra"}
    assert esperados <= slugs, f"faltando: {esperados - slugs}"

    for h in result.habilidades:
        assert h["titulo"], "título não pode estar vazio"
        assert h["descricao"], f"{h['slug']} sem descrição"


# ─── Loader + API ────────────────────────────────────────────────────────


def test_loader_resolve_habilidade_por_slug():
    item = get_habilidade_by_slug("furia")
    if not list_habilidades():
        pytest.skip("catálogo ausente no ambiente")
    assert item is not None
    assert item["titulo"].lower().startswith("fúria") or item["titulo"].lower().startswith("furia")


def test_loader_resolve_por_texto_remove_parenteses():
    if not list_habilidades():
        pytest.skip("catálogo ausente no ambiente")
    item = resolver_por_texto("Fúria (1/dia)")
    assert item is not None
    assert item["slug"] == "furia"


def test_loader_resolve_por_texto_prefixo_maior_vence():
    if not list_habilidades():
        pytest.skip("catálogo ausente no ambiente")
    item = resolver_por_texto("Esquiva sobrenatural aprimorada")
    assert item is not None
    assert item["slug"] == "esquiva-sobrenatural-aprimorada"


def _client() -> TestClient:
    app = FastAPI()
    app.include_router(habilidades_router, prefix="/api/v1")
    return TestClient(app)


def test_api_listar_habilidades_especiais():
    if not list_habilidades():
        pytest.skip("catálogo ausente no ambiente")
    client = _client()
    response = client.get("/api/v1/habilidades-especiais")
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body, list)
    assert any(item.get("slug") == "furia" for item in body)
    item = next(i for i in body if i["slug"] == "furia")
    assert set(item.keys()) == {"slug", "titulo"}


def test_api_obter_habilidade_por_slug():
    if not list_habilidades():
        pytest.skip("catálogo ausente no ambiente")
    client = _client()
    response = client.get("/api/v1/habilidades-especiais/furia")
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "furia"
    assert body["descricao"]
    assert "aliases" in body


def test_api_obter_habilidade_404_para_slug_invalido():
    client = _client()
    response = client.get("/api/v1/habilidades-especiais/nao-existe-12345")
    assert response.status_code == 404
