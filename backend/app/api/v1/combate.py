"""
Controller/Router de Combate
Princípio SOLID: SRP - Responsável apenas por HTTP routing
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.dependencies import get_combate_service
from ...services.combate_service import CombateService
from ...schemas.combate import (
    IniciarCombateRequest,
    CombateResponse,
    AplicarDanoRequest
)
from ...exceptions.custom_exceptions import ArenaBaseException


router = APIRouter(prefix="/combate", tags=["Combate"])


@router.post("/iniciar")
def iniciar_combate(
    request: IniciarCombateRequest,
    db: Session = Depends(get_db)
):
    """Inicia um novo combate"""
    service = get_combate_service(db)
    try:
        combate = service.iniciar_combate(request.combatente_ids)
        status = service.obter_status_combate()
        return status
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/status")
def status_combate(db: Session = Depends(get_db)):
    """Obtém o status do combate ativo"""
    service = get_combate_service(db)
    return service.obter_status_combate()


@router.post("/avancar-turno")
def avancar_turno(db: Session = Depends(get_db)):
    """Avança para o próximo turno"""
    service = get_combate_service(db)
    try:
        service.avancar_turno()
        status = service.obter_status_combate()
        return status
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/aplicar-dano")
def aplicar_dano(
    request: AplicarDanoRequest,
    db: Session = Depends(get_db)
):
    """Aplica dano a um combatente durante o combate"""
    from ...core.dependencies import get_combatente_service
    
    combatente_service = get_combatente_service(db)
    try:
        combatente = combatente_service.aplicar_dano(request.combatente_id, request.dano)
        return combatente
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/finalizar")
def finalizar_combate(db: Session = Depends(get_db)):
    """Finaliza o combate ativo"""
    service = get_combate_service(db)
    try:
        service.finalizar_combate()
        return {"message": "Combate finalizado com sucesso"}
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/resetar")
def resetar_combate(db: Session = Depends(get_db)):
    """Reseta todos os combatentes e finaliza o combate"""
    service = get_combate_service(db)
    try:
        result = service.resetar_combate()
        return result
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)