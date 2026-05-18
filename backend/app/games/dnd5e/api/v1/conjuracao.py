"""HTTP — conjuração na ficha (slots, descanso, preparação)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_dnd5e_conjuracao_ficha_service
from app.games.dnd5e.schemas.conjuracao import (
    Dnd5eConjuracaoDescansoResponse,
    Dnd5eConjuracaoEstadoResponse,
    Dnd5eConjuracaoGastarSlotRequest,
    Dnd5eConjuracaoPrepararRequest,
)
from app.games.dnd5e.services.conjuracao_ficha_service import Dnd5eConjuracaoFichaService
from app.shared.core.deps import requer_dono_ou_admin_dnd5e_personagem, requer_game_dnd5e

router = APIRouter(
    prefix="/dnd5e/personagens",
    tags=["D&D 5e — Conjuração (ficha)"],
    dependencies=[Depends(requer_game_dnd5e)],
)


@router.get(
    "/{personagem_id}/conjuracao",
    response_model=Dnd5eConjuracaoEstadoResponse,
)
def obter_conjuracao_ficha(
    personagem_id: int,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    return service.obter_estado(personagem_id)


@router.post(
    "/{personagem_id}/conjuracao/gastar-slot",
    response_model=Dnd5eConjuracaoEstadoResponse,
)
def gastar_slot_conjuracao(
    personagem_id: int,
    payload: Dnd5eConjuracaoGastarSlotRequest,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    return service.gastar_slot(
        personagem_id, payload.nivel_magia, payload.quantidade
    )


@router.put(
    "/{personagem_id}/conjuracao/preparar",
    response_model=Dnd5eConjuracaoEstadoResponse,
)
def preparar_magias_conjuracao(
    personagem_id: int,
    payload: Dnd5eConjuracaoPrepararRequest,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    return service.preparar_magias(personagem_id, payload.magia_ids)


@router.post(
    "/{personagem_id}/conjuracao/descanso-longo",
    response_model=Dnd5eConjuracaoDescansoResponse,
)
def descanso_longo_conjuracao(
    personagem_id: int,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    estado = service.descanso_longo(personagem_id)
    return Dnd5eConjuracaoDescansoResponse(
        estado=estado,
        mensagem="Descanso longo: slots restaurados e preparação limpa.",
    )


@router.post(
    "/{personagem_id}/conjuracao/descanso-curto",
    response_model=Dnd5eConjuracaoDescansoResponse,
)
def descanso_curto_conjuracao(
    personagem_id: int,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    estado = service.descanso_curto(personagem_id)
    return Dnd5eConjuracaoDescansoResponse(
        estado=estado, mensagem="Repouso curto: slots restaurados."
    )
