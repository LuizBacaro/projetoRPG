"""
Endpoints read-only do catálogo de tabelas de classes (experimental) — D&D 3.5.

Canônico em `app.games.dnd35.api.v1.tabelas_classes` (registrado em `app.main`).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query

from app.shared.core.catalog_cache import catalog_cache, make_cache_key
from app.core.config import settings
from app.shared.core.deps import get_usuario_atual
from app.games.dnd35.schemas.tabelas_classes import (
    TabelaClassesResponse,
    TabelasClassesListResponse,
)
from app.games.dnd35.services.tabelas_classes_service import TabelasClassesService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tabelas-classes", tags=["Tabelas Classes"])


def _require_feature_enabled() -> None:
    if not settings.CLASSES_TABLES_CATALOG_ENABLED:
        # Mantém rollout seguro: endpoint existe, mas não expõe funcionalidade.
        raise HTTPException(status_code=404, detail="Recurso não habilitado")


@router.get("/", response_model=TabelasClassesListResponse)
def listar_tabelas_classes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    table_number: int | None = Query(default=None, ge=3, le=18),
    _: object = Depends(get_usuario_atual),
) -> TabelasClassesListResponse:
    _require_feature_enabled()
    try:
        cache_key = make_cache_key(
            "tabelas_classes:list",
            skip=skip,
            limit=limit,
            table_number=table_number,
        )
        if settings.CACHE_ENABLED:
            cached = catalog_cache.get(cache_key)
            if cached is not None:
                return cached

        service = TabelasClassesService()
        response = service.listar_tabelas(skip=skip, limit=limit, table_number=table_number)
        if settings.CACHE_ENABLED:
            catalog_cache.set(cache_key, response, settings.CACHE_CATALOG_TTL_SECONDS)
        return response
    except Exception as exc:
        logger.error("Erro ao listar tabelas de classes: %s", exc)
        raise HTTPException(status_code=500, detail="Erro ao listar tabelas de classes")


@router.get("/{table_number}", response_model=TabelaClassesResponse)
def obter_tabela_classes(table_number: int, _: object = Depends(get_usuario_atual)) -> TabelaClassesResponse:
    _require_feature_enabled()
    try:
        cache_key = make_cache_key("tabelas_classes:detail", table_number=table_number)
        if settings.CACHE_ENABLED:
            cached = catalog_cache.get(cache_key)
            if cached is not None:
                return cached

        service = TabelasClassesService()
        table = service.obter_tabela(table_number)
        if table is None:
            raise HTTPException(status_code=404, detail="Tabela não encontrada")
        if settings.CACHE_ENABLED:
            catalog_cache.set(cache_key, table, settings.CACHE_CATALOG_TTL_SECONDS)
        return table
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Erro ao obter tabela de classes %s: %s", table_number, exc)
        raise HTTPException(status_code=500, detail="Erro ao obter tabela de classes")
