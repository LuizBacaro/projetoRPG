"""HTTP — personagens Tormenta 20 (ficha Módulo Básico)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.core.dependencies import get_tormenta_personagem_service
from app.games.tormenta.schemas.personagem import (
    TormentaPersonagemCreate,
    TormentaPersonagemResponse,
    TormentaPersonagemUpdate,
)
from app.games.tormenta.services.personagem_service import TormentaPersonagemService
from app.shared.core.deps import (
    get_usuario_atual,
    requer_dono_ou_admin_tormenta_personagem,
    requer_game_tormenta,
)
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/tormenta/personagens",
    tags=["Tormenta — Personagens"],
    dependencies=[Depends(requer_game_tormenta)],
)


@router.get("", response_model=List[TormentaPersonagemResponse])
def listar(
    tipo: Optional[str] = None,
    meus: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    response: Response = None,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    total = service.contar_todos(tipo, usuario=usuario_atual, apenas_meus=meus)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)
    return service.listar_todos(
        tipo,
        usuario=usuario_atual,
        skip=skip,
        limit=limit,
        apenas_meus=meus,
    )


@router.get("/{personagem_id}", response_model=TormentaPersonagemResponse)
def obter(
    personagem_id: int,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        ent = service.obter_por_id(personagem_id)
        return TormentaPersonagemResponse.model_validate(ent)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("", response_model=TormentaPersonagemResponse, status_code=201)
def criar(
    payload: TormentaPersonagemCreate,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        return service.criar(usuario_atual, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        code = getattr(e, "status_code", 400)
        raise HTTPException(status_code=code, detail=getattr(e, "message", str(e)))


@router.patch("/{personagem_id}", response_model=TormentaPersonagemResponse)
def atualizar(
    personagem_id: int,
    payload: TormentaPersonagemUpdate,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        return service.atualizar(personagem_id, payload)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=e.message)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/{personagem_id}", status_code=204)
def excluir(
    personagem_id: int,
    service: TormentaPersonagemService = Depends(get_tormenta_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_tormenta_personagem),
):
    try:
        service.excluir(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
