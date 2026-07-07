"""HTTP — combate GURPS (Arena)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_gurps_combate_service
from app.games.gurps.schemas.combate import (
    GurpsAjustePvRequest,
    GurpsAtaqueRequest,
    GurpsDefinirManobraRequest,
    GurpsDefinirPosturaRequest,
    GurpsEsforcoRequest,
    GurpsIniciarCombateRequest,
)
from app.games.gurps.services.combate_service import GurpsCombateService
from app.shared.core.database import get_db
from app.shared.core.deps import (
    get_usuario_atual,
    requer_game_gurps,
    requer_mestre_gurps_ou_admin,
    validar_gurps_personagens_do_usuario,
)
from app.shared.exceptions.custom_exceptions import ArenaBaseException
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/gurps/combate",
    tags=["GURPS — Combate"],
    dependencies=[Depends(requer_game_gurps), Depends(requer_mestre_gurps_ou_admin)],
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


@router.post("/manobra-atual")
def definir_manobra_atual(
    body: GurpsDefinirManobraRequest,
    service: GurpsCombateService = Depends(get_gurps_combate_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        service.definir_manobra_ativa(body.manobra)
        return service.obter_status_combate()
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/postura-atual")
def definir_postura_atual(
    body: GurpsDefinirPosturaRequest,
    service: GurpsCombateService = Depends(get_gurps_combate_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        service.definir_postura_ativa(body.postura)
        return service.obter_status_combate()
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/ataque")
def executar_ataque(
    body: GurpsAtaqueRequest,
    service: GurpsCombateService = Depends(get_gurps_combate_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        return service.executar_ataque(
            body.alvo_id,
            body.nh_ataque,
            body.tipo_ataque,
            body.tipo_defesa,
            body.expressao_dano,
            dados_ataque=body.dados_ataque,
            dados_defesa=body.dados_defesa,
            dados_dano=body.dados_dano,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/ajustar-pv")
def ajustar_pv(
    body: GurpsAjustePvRequest,
    service: GurpsCombateService = Depends(get_gurps_combate_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        return service.ajustar_pv_alvo(body.alvo_id, body.delta_pv)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/esforco")
def aplicar_esforco(
    body: GurpsEsforcoRequest,
    service: GurpsCombateService = Depends(get_gurps_combate_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        return service.aplicar_esforco_ativo(
            custo_fadiga=body.custo_fadiga,
            usar_surto=body.usar_surto,
            descricao=body.descricao,
        )
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
