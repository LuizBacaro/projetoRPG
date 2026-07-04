"""HTTP — combate Tormenta 20 (Arena)."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.dependencies import get_tormenta_combate_service
from app.games.tormenta.schemas.combate import (
    TormentaCombateCondicoesMbRequest,
    TormentaCombateRolarAtaqueRequest,
    TormentaCombateRolarDanoRequest,
    TormentaCombateRolarIniciativaRequest,
    TormentaCombateTestarResistenciaMagiaRequest,
    TormentaIniciarCombateRequest,
)
from app.games.tormenta.services.combate_service import TormentaCombateService
from app.shared.core.database import get_db
from app.shared.core.deps import (
    get_usuario_atual,
    requer_game_tormenta,
    requer_mestre_ou_admin,
    validar_tormenta_personagens_do_usuario,
)
from app.shared.exceptions.custom_exceptions import ArenaBaseException
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/tormenta/combate",
    tags=["Tormenta — Arena"],
    dependencies=[Depends(requer_game_tormenta), Depends(requer_mestre_ou_admin)],
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


@router.post("/rolar-iniciativa")
def rolar_iniciativa(
    body: TormentaCombateRolarIniciativaRequest,
    service: TormentaCombateService = Depends(get_tormenta_combate_service),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        validar_tormenta_personagens_do_usuario(body.personagem_ids, usuario_atual, db)
        result = service.rolar_iniciativa_combate(body.personagem_ids)
        return {**result, "status": service.obter_status_combate()}
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/rolar-ataque")
def rolar_ataque(
    body: TormentaCombateRolarAtaqueRequest,
    service: TormentaCombateService = Depends(get_tormenta_combate_service),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        validar_tormenta_personagens_do_usuario(
            [body.atacante_id, body.alvo_id], usuario_atual, db
        )
        return service.rolar_ataque_combate(
            body.atacante_id,
            body.alvo_id,
            body.bab,
            body.mod_atributo,
            bonus_arma=body.bonus_arma,
            penalidades=body.penalidades,
            ca_alvo=body.ca_alvo,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/rolar-dano")
def rolar_dano(
    body: TormentaCombateRolarDanoRequest,
    service: TormentaCombateService = Depends(get_tormenta_combate_service),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        if body.aplicar_ao_alvo_id is not None:
            validar_tormenta_personagens_do_usuario(
                [body.aplicar_ao_alvo_id], usuario_atual, db
            )
        return service.rolar_dano_combate(
            body.formula_dano,
            mod_atributo=body.mod_atributo,
            confirmar_critico=body.confirmar_critico,
            aplicar_ao_id=body.aplicar_ao_alvo_id,
            atacante_id=body.atacante_id,
            forca_dos_titas=body.forca_dos_titas,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/testar-resistencia-magia")
def testar_resistencia_magia(
    body: TormentaCombateTestarResistenciaMagiaRequest,
    service: TormentaCombateService = Depends(get_tormenta_combate_service),
    db: Session = Depends(get_db),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        ids = [body.alvo_id]
        if body.conjurador_id is not None:
            ids.append(body.conjurador_id)
        validar_tormenta_personagens_do_usuario(ids, usuario_atual, db)
        return service.testar_resistencia_magia_combate(
            alvo_id=body.alvo_id,
            tipo=body.tipo or "",
            cd=body.cd,
            circulo_magia=body.circulo_magia,
            conjurador_id=body.conjurador_id,
            magia_slug=body.magia_slug,
            falha_voluntaria=body.falha_voluntaria,
            efeito_mental=body.efeito_mental,
        )
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
