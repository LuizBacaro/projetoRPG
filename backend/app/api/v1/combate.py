"""
Controller/Router de Combate
Princípio SOLID: SRP - Responsável apenas por HTTP routing
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.deps import get_usuario_atual, validar_combatentes_do_usuario
from ...core.dependencies import get_combate_service
from ...services.combate_service import CombateService
from ...models.usuario import Usuario
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
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    """Inicia um novo combate"""
    service = get_combate_service(db)
    try:
        validar_combatentes_do_usuario(request.combatente_ids, usuario_atual, db)
        combate = service.iniciar_combate(request.combatente_ids)
        status = service.obter_status_combate()
        return status
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/status")
def status_combate(db: Session = Depends(get_db), _: object = Depends(get_usuario_atual)):
    """Obtém o status do combate ativo"""
    service = get_combate_service(db)
    return service.obter_status_combate()


@router.post("/avancar-turno")
def avancar_turno(db: Session = Depends(get_db), _: object = Depends(get_usuario_atual)):
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
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    """Aplica dano a um combatente durante o combate"""
    from ...core.dependencies import get_combatente_service
    
    combatente_service = get_combatente_service(db)
    try:
        validar_combatentes_do_usuario([request.combatente_id], usuario_atual, db)
        combatente = combatente_service.aplicar_dano(request.combatente_id, request.dano)
        return combatente
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/finalizar")
def finalizar_combate(db: Session = Depends(get_db), _: object = Depends(get_usuario_atual)):
    """Finaliza o combate ativo"""
    service = get_combate_service(db)
    try:
        service.finalizar_combate()
        return {"message": "Combate finalizado com sucesso"}
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/resetar")
def resetar_combate(db: Session = Depends(get_db), _: object = Depends(get_usuario_atual)):
    """Reseta todos os combatentes e finaliza o combate"""
    service = get_combate_service(db)
    try:
        result = service.resetar_combate()
        return result
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)