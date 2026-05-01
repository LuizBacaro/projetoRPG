"""HTTP — combate GURPS (Arena)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_gurps_combate_service
from app.games.gurps.schemas.combate import GurpsIniciarCombateRequest
from app.games.gurps.services.combate_service import GurpsCombateService
from app.shared.core.database import get_db
from app.shared.core.deps import (
    get_usuario_atual,
    requer_game_gurps,
    validar_gurps_personagens_do_usuario,
)
from app.shared.exceptions.custom_exceptions import ArenaBaseException
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/gurps/combate",
    tags=["GURPS — Combate"],
    dependencies=[Depends(requer_game_gurps)],
)


@router.post("/iniciar")
def iniciar(
    body: GurpsIniciarCombateRequest,
    service: GurpsCombateService = Depends(get_gurps_combate_service),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        validar_gurps_personagens_do_usuario(body.personagem_ids, usuario_atual, db)
        service.iniciar_combate(body.personagem_ids)
        return service.obter_status_combate()
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/status")
def status(
    resumido: bool = Query(False),
    service: GurpsCombateService = Depends(get_gurps_combate_service),
    _: object = Depends(get_usuario_atual),
):
    return service.obter_status_combate(incluir_personagens=not resumido)


@router.post("/avancar-turno")
def avancar_turno(
    service: GurpsCombateService = Depends(get_gurps_combate_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        service.avancar_turno()
        return service.obter_status_combate()
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/finalizar")
def finalizar(
    service: GurpsCombateService = Depends(get_gurps_combate_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        service.finalizar_combate()
        return service.obter_status_combate()
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
