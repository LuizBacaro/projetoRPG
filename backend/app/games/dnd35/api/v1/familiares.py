import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_familiar_service
from app.games.dnd35.schemas.familiar import (
    FamiliarCalcularRequest,
    FamiliarCalcularResponse,
    FamiliarElegibilidadeResponse,
    FamiliarEspecieItem,
    FamiliarResponse,
    FamiliarUpsert,
)
from app.games.dnd35.services.familiar_service import FamiliarService
from app.shared.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.shared.exceptions.custom_exceptions import CombatenteNaoEncontrado

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/familiares", tags=["Familiares"])


@router.get("/especies", response_model=list[FamiliarEspecieItem])
def listar_especies(
    service: FamiliarService = Depends(get_familiar_service),
    _: object = Depends(get_usuario_atual),
):
    return service.listar_especies()


@router.get(
    "/{combatente_id}/elegibilidade", response_model=FamiliarElegibilidadeResponse
)
def elegibilidade(
    combatente_id: int,
    service: FamiliarService = Depends(get_familiar_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.elegibilidade(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{combatente_id}/calcular", response_model=FamiliarCalcularResponse)
def calcular(
    combatente_id: int,
    payload: FamiliarCalcularRequest,
    service: FamiliarService = Depends(get_familiar_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.calcular(combatente_id, payload)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{combatente_id}", response_model=FamiliarResponse | None)
def obter(
    combatente_id: int,
    service: FamiliarService = Depends(get_familiar_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.obter(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{combatente_id}", response_model=FamiliarResponse)
def salvar(
    combatente_id: int,
    payload: FamiliarUpsert,
    service: FamiliarService = Depends(get_familiar_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.salvar(combatente_id, payload)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/{combatente_id}/criar-rapido",
    response_model=FamiliarResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_rapido(
    combatente_id: int,
    payload: FamiliarCalcularRequest,
    service: FamiliarService = Depends(get_familiar_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.criar_a_partir_calculo(combatente_id, payload)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{combatente_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(
    combatente_id: int,
    service: FamiliarService = Depends(get_familiar_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        ok = service.remover(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="Familiar não cadastrado")
    return None
