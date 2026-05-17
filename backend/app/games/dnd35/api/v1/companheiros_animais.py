import logging

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_companheiro_animal_service
from app.games.dnd35.schemas.companheiro_animal import (
    CompanheiroAnimalResponse,
    CompanheiroAnimalUpsert,
    CompanheiroCalcularRequest,
    CompanheiroCalcularResponse,
    CompanheiroElegibilidadeResponse,
    CompanheiroEspecieItem,
)
from app.games.dnd35.services.companheiro_animal_service import CompanheiroAnimalService
from app.shared.core.deps import (
    get_usuario_atual,
    requer_dono_ou_admin_combatente,
)
from app.shared.exceptions.custom_exceptions import CombatenteNaoEncontrado

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/companheiros-animais", tags=["Companheiros Animais"])


@router.get("/especies", response_model=list[CompanheiroEspecieItem])
def listar_especies(
    service: CompanheiroAnimalService = Depends(get_companheiro_animal_service),
    _: object = Depends(get_usuario_atual),
):
    return service.listar_especies()


@router.get(
    "/{combatente_id}/elegibilidade",
    response_model=CompanheiroElegibilidadeResponse,
)
def elegibilidade(
    combatente_id: int,
    service: CompanheiroAnimalService = Depends(get_companheiro_animal_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.elegibilidade(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/{combatente_id}/calcular",
    response_model=CompanheiroCalcularResponse,
)
def calcular(
    combatente_id: int,
    payload: CompanheiroCalcularRequest,
    service: CompanheiroAnimalService = Depends(get_companheiro_animal_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.calcular(combatente_id, payload)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{combatente_id}",
    response_model=CompanheiroAnimalResponse | None,
)
def obter(
    combatente_id: int,
    service: CompanheiroAnimalService = Depends(get_companheiro_animal_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """200 com corpo null quando ainda não há companheiro (evita 404 no carregamento da ficha)."""
    try:
        return service.obter(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put(
    "/{combatente_id}",
    response_model=CompanheiroAnimalResponse,
)
def salvar(
    combatente_id: int,
    payload: CompanheiroAnimalUpsert,
    service: CompanheiroAnimalService = Depends(get_companheiro_animal_service),
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
    response_model=CompanheiroAnimalResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_rapido(
    combatente_id: int,
    payload: CompanheiroCalcularRequest,
    service: CompanheiroAnimalService = Depends(get_companheiro_animal_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.criar_a_partir_calculo(combatente_id, payload, payload.nome)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{combatente_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(
    combatente_id: int,
    service: CompanheiroAnimalService = Depends(get_companheiro_animal_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        ok = service.remover(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))
    if not ok:
        raise HTTPException(status_code=404, detail="Companheiro animal não cadastrado")
    return None
