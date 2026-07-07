"""
Controller/Router de Combate
Princípio SOLID: SRP - Responsável apenas por HTTP routing

Canônico em `app.games.dnd35.api.v1.combate` (registrado em `app.main`).
"""

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import (
    get_combate_service,
    get_combatente_service,
    get_condicao_service,
    get_vinculo_arena_service,
)
from app.games.dnd35.schemas.combate import (
    AplicarDanoRequest,
    CombateHistoricoListResponse,
    IniciarCombateRequest,
)
from app.games.dnd35.services.combate_service import CombateService
from app.games.dnd35.services.combatente_service import CombatenteService
from app.games.dnd35.services.condicao_service import CondicaoService
from app.games.dnd35.services.vinculo_arena_service import VinculoArenaService
from app.shared.core.database import get_db
from app.shared.core.deps import (
    get_usuario_atual,
    requer_game_dnd35,
    requer_mestre_dnd35_ou_admin,
    validar_combatentes_do_usuario,
)
from app.shared.exceptions.custom_exceptions import ArenaBaseException
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/combate",
    tags=["Combate"],
    dependencies=[Depends(requer_game_dnd35), Depends(requer_mestre_dnd35_ou_admin)],
)


@router.post("/iniciar")
def iniciar_combate(
    request: IniciarCombateRequest,
    service: CombateService = Depends(get_combate_service),
    vinculo_arena: VinculoArenaService = Depends(get_vinculo_arena_service),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    """Inicia um novo combate"""
    try:
        ids = vinculo_arena.expandir_combatente_ids(
            request.combatente_ids,
            incluir_vinculos=request.incluir_vinculos,
        )
        validar_combatentes_do_usuario(ids, usuario_atual, db)
        combate = service.iniciar_combate(ids)
        status = service.obter_status_combate()
        return status
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/status")
def status_combate(
    resumido: bool = Query(False),
    service: CombateService = Depends(get_combate_service),
    _: object = Depends(get_usuario_atual),
):
    """Obtém o status do combate ativo"""
    return service.obter_status_combate(incluir_combatentes=not resumido)


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
    resumido: bool = Query(False),
    service: CombateService = Depends(get_combate_service),
    condicao_service: CondicaoService = Depends(get_condicao_service),
    if_match: str = Header(default=None, alias="If-Match"),
    _: object = Depends(get_usuario_atual),
):
    """Avança para o próximo turno"""
    try:
        combate = service.avancar_turno(if_match, condicao_service=condicao_service)
        return service.montar_status_combate(combate, incluir_combatentes=not resumido)
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
def resetar_combate(
    service: CombateService = Depends(get_combate_service),
    _: object = Depends(get_usuario_atual),
):
    """Reseta todos os combatentes e finaliza o combate"""
    try:
        result = service.resetar_combate()
        return result
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
