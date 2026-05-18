"""HTTP — catálogo de magias D&D 5e."""

from __future__ import annotations

from io import BytesIO
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from fastapi.responses import StreamingResponse

from app.core.dependencies import get_dnd5e_magia_import_service, get_dnd5e_magia_service
from app.games.dnd5e.schemas.grimorio import (
    Dnd5eMagiaImportConfirmRequest,
    Dnd5eMagiaImportConfirmResponse,
    Dnd5eMagiaImportPreviewResponse,
)
from app.games.dnd5e.schemas.magia import Dnd5eMagiaListResponse, Dnd5eMagiaResponse
from app.games.dnd5e.services.magia_import_service import Dnd5eMagiaImportService
from app.games.dnd5e.services.magia_service import Dnd5eMagiaService
from app.shared.core.deps import requer_game_dnd5e, requer_mestre_ou_admin

router = APIRouter(
    prefix="/dnd5e/magias",
    tags=["D&D 5e — Magias"],
    dependencies=[Depends(requer_game_dnd5e)],
)


@router.get("", response_model=Dnd5eMagiaListResponse)
def listar_magias(
    nome: Optional[str] = Query(default=None),
    nivel: Optional[int] = Query(default=None, ge=0, le=9),
    escola: Optional[str] = Query(default=None),
    classe_slug: Optional[str] = Query(default=None, alias="classe"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    response: Response = None,
    service: Dnd5eMagiaService = Depends(get_dnd5e_magia_service),
):
    total, magias = service.listar(
        nome=nome,
        nivel=nivel,
        escola=escola,
        classe_slug=classe_slug,
        skip=skip,
        limit=limit,
    )
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)
    return Dnd5eMagiaListResponse(magias=magias, total=total)


@router.get("/{magia_id}", response_model=Dnd5eMagiaResponse)
def obter_magia(
    magia_id: int,
    service: Dnd5eMagiaService = Depends(get_dnd5e_magia_service),
):
    magia = service.obter(magia_id)
    if not magia:
        raise HTTPException(status_code=404, detail="Magia não encontrada")
    return magia


@router.get("/importacao/modelo")
def baixar_modelo_importacao_magias(
    service: Dnd5eMagiaImportService = Depends(get_dnd5e_magia_import_service),
    _: object = Depends(requer_mestre_ou_admin),
):
    content = service.gerar_modelo()
    return StreamingResponse(
        BytesIO(content),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": 'attachment; filename="modelo_magias_dnd5e.xlsx"'
        },
    )


@router.post("/importacao/preview", response_model=Dnd5eMagiaImportPreviewResponse)
async def preview_importacao_magias(
    arquivo: UploadFile = File(...),
    service: Dnd5eMagiaImportService = Depends(get_dnd5e_magia_import_service),
    _: object = Depends(requer_mestre_ou_admin),
):
    return await service.preview(arquivo)


@router.post(
    "/importacao/confirmar", response_model=Dnd5eMagiaImportConfirmResponse
)
def confirmar_importacao_magias(
    payload: Dnd5eMagiaImportConfirmRequest,
    service: Dnd5eMagiaImportService = Depends(get_dnd5e_magia_import_service),
    _: object = Depends(requer_mestre_ou_admin),
):
    return service.confirmar(payload.import_id)
