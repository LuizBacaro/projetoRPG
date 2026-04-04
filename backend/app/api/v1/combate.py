"""
Controller/Router de Combate
Princípio SOLID: SRP - Responsável apenas por HTTP routing
"""
from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from ...core.database import get_db
from ...core.deps import get_usuario_atual, validar_combatentes_do_usuario
from ...core.dependencies import get_combate_service, get_combatente_service
from ...services.combate_service import CombateService
from ...services.combatente_service import CombatenteService
from ...models.usuario import Usuario
from ...schemas.combate import (
    IniciarCombateRequest,
    CombateResponse,
    AplicarDanoRequest,
    CombateHistoricoListResponse,
)
from ...exceptions.custom_exceptions import ArenaBaseException


router = APIRouter(prefix="/combate", tags=["Combate"])


@router.post("/iniciar")
def iniciar_combate(
    request: IniciarCombateRequest,
    service: CombateService = Depends(get_combate_service),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    """Inicia um novo combate"""
    try:
        validar_combatentes_do_usuario(request.combatente_ids, usuario_atual, db)
        combate = service.iniciar_combate(request.combatente_ids)
        status = service.obter_status_combate()
        return status
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/status")
def status_combate(service: CombateService = Depends(get_combate_service), _: object = Depends(get_usuario_atual)):
    """Obtém o status do combate ativo"""
    return service.obter_status_combate()


@router.get("/historico", response_model=CombateHistoricoListResponse)
def listar_historico(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    service: CombateService = Depends(get_combate_service),
    _: object = Depends(get_usuario_atual),
):
    """Lista histórico de combates finalizados com estatísticas consolidadas."""
    return service.listar_historico(skip=skip, limit=limit)


@router.post("/avancar-turno")
def avancar_turno(
    service: CombateService = Depends(get_combate_service),
    if_match: str = Header(default=None, alias="If-Match"),
    _: object = Depends(get_usuario_atual),
):
    """Avança para o próximo turno"""
    try:
        service.avancar_turno(if_match)
        status = service.obter_status_combate()
        return status
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/aplicar-dano")
def aplicar_dano(
    request: AplicarDanoRequest,
    service: CombatenteService = Depends(get_combatente_service),
    combate_service: CombateService = Depends(get_combate_service),
    if_match: str = Header(default=None, alias="If-Match"),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    """Aplica dano a um combatente durante o combate"""
    try:
        combate_ativo = combate_service.obter_combate_ativo()
        if combate_ativo:
            combate_service.validar_versao(if_match, combate_ativo)
        validar_combatentes_do_usuario([request.combatente_id], usuario_atual, db)
        combatente = service.aplicar_dano(request.combatente_id, request.dano)
        return combatente
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/finalizar")
def finalizar_combate(
    service: CombateService = Depends(get_combate_service),
    if_match: str = Header(default=None, alias="If-Match"),
    _: object = Depends(get_usuario_atual),
):
    """Finaliza o combate ativo"""
    try:
        service.finalizar_combate(if_match)
        return {"message": "Combate finalizado com sucesso"}
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/resetar")
def resetar_combate(service: CombateService = Depends(get_combate_service), _: object = Depends(get_usuario_atual)):
    """Reseta todos os combatentes e finaliza o combate"""
    try:
        result = service.resetar_combate()
        return result
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)