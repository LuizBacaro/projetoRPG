"""HTTP — combate Tormenta 20 (Arena)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_tormenta_combate_service
from app.games.tormenta.schemas.combate import (
    TormentaCombateCondicoesMbRequest,
    TormentaIniciarCombateRequest,
)
from app.games.tormenta.services.combate_service import TormentaCombateService
from app.shared.core.database import get_db
from app.shared.core.deps import (
    get_usuario_atual,
    requer_game_tormenta,
    validar_tormenta_personagens_do_usuario,
)
from app.shared.exceptions.custom_exceptions import ArenaBaseException
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/tormenta/combate",
    tags=["Tormenta — Arena"],
    dependencies=[Depends(requer_game_tormenta)],
)


@router.post("/iniciar")
def iniciar(
    body: TormentaIniciarCombateRequest,
    service: TormentaCombateService = Depends(get_tormenta_combate_service),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        validar_tormenta_personagens_do_usuario(body.personagem_ids, usuario_atual, db)
        service.iniciar_combate(body.personagem_ids)
        return service.obter_status_combate()
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get("/status")
def status(
    resumido: bool = Query(False),
    service: TormentaCombateService = Depends(get_tormenta_combate_service),
    _: object = Depends(get_usuario_atual),
):
    return service.obter_status_combate(incluir_personagens=not resumido)


@router.post("/avancar-turno")
def avancar_turno(
    service: TormentaCombateService = Depends(get_tormenta_combate_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        service.avancar_turno()
        return service.obter_status_combate()
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/condicoes-mb")
def aplicar_condicoes_mb(
    body: TormentaCombateCondicoesMbRequest,
    service: TormentaCombateService = Depends(get_tormenta_combate_service),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        ids = [int(k) for k in body.por_personagem.keys()]
        validar_tormenta_personagens_do_usuario(ids, usuario_atual, db)
        service.aplicar_condicoes_mb(body.por_personagem)
        return service.obter_status_combate()
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/finalizar")
def finalizar(
    service: TormentaCombateService = Depends(get_tormenta_combate_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        service.finalizar_combate()
        return service.obter_status_combate()
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
