"""HTTP — conjuração na ficha (slots, descanso, preparação)."""

from __future__ import annotations

from fastapi import APIRouter, Depends

from app.core.dependencies import get_dnd5e_conjuracao_ficha_service
from app.games.dnd5e.schemas.conjuracao import (
    Dnd5eConjuracaoConcentracaoRequest,
    Dnd5eConjuracaoDescansoResponse,
    Dnd5eConjuracaoEstadoResponse,
    Dnd5eConjuracaoGastarSlotRequest,
    Dnd5eConjuracaoPrepararRequest,
    Dnd5ePontosFeiticariaConverterSlotRequest,
    Dnd5ePontosFeiticariaCriarSlotRequest,
    Dnd5eRecuperacaoArcanaRequest,
)
from app.games.dnd5e.services.conjuracao_ficha_service import (
    Dnd5eConjuracaoFichaService,
)
from app.shared.core.deps import (
    requer_dono_ou_admin_dnd5e_personagem,
    requer_game_dnd5e,
)

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
        personagem_id,
        payload.nivel_magia,
        payload.quantidade,
        magia_id=payload.magia_id,
    )


@router.post(
    "/{personagem_id}/conjuracao/devolver-slot",
    response_model=Dnd5eConjuracaoEstadoResponse,
    summary="Devolve um espaço de magia previamente gasto (arena)",
)
def devolver_slot_conjuracao(
    personagem_id: int,
    payload: Dnd5eConjuracaoGastarSlotRequest,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    return service.devolver_slot(
        personagem_id,
        payload.nivel_magia,
        payload.quantidade,
        magia_id=payload.magia_id,
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
    return service.preparar_magias(
        personagem_id,
        payload.magia_ids,
        payload.magias_quantidade or None,
    )


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
    msg = (
        "Repouso curto: slots restaurados."
        if estado.recupera_slots_repouso_curto
        else "Repouso curto registrado (Mago: use Recuperação Arcana)."
    )
    return Dnd5eConjuracaoDescansoResponse(estado=estado, mensagem=msg)


@router.post(
    "/{personagem_id}/conjuracao/pontos-feiticaria/criar-slot",
    response_model=Dnd5eConjuracaoEstadoResponse,
    summary="Feiticeiro: gasta pontos de feitiçaria para criar um espaço",
)
def criar_slot_pontos_feiticaria(
    personagem_id: int,
    payload: Dnd5ePontosFeiticariaCriarSlotRequest,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    return service.criar_slot_pontos_feiticaria(personagem_id, payload.nivel_slot)


@router.post(
    "/{personagem_id}/conjuracao/pontos-feiticaria/converter",
    response_model=Dnd5eConjuracaoEstadoResponse,
    summary="Feiticeiro: converte espaço em pontos de feitiçaria",
)
def converter_slot_pontos_feiticaria(
    personagem_id: int,
    payload: Dnd5ePontosFeiticariaConverterSlotRequest,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    return service.converter_slot_pontos_feiticaria(personagem_id, payload.nivel_slot)


@router.post(
    "/{personagem_id}/conjuracao/recuperacao-arcana",
    response_model=Dnd5eConjuracaoEstadoResponse,
    summary="Mago: recuperação arcana após repouso curto (1× por descanso longo)",
)
def recuperacao_arcana_conjuracao(
    personagem_id: int,
    payload: Dnd5eRecuperacaoArcanaRequest,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    return service.recuperacao_arcana(personagem_id, payload.slots)


@router.put(
    "/{personagem_id}/conjuracao/concentracao",
    response_model=Dnd5eConjuracaoEstadoResponse,
    summary="Define ou limpa a magia em concentração na ficha",
)
def definir_concentracao_conjuracao(
    personagem_id: int,
    payload: Dnd5eConjuracaoConcentracaoRequest,
    service: Dnd5eConjuracaoFichaService = Depends(get_dnd5e_conjuracao_ficha_service),
    _: object = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    return service.definir_concentracao(personagem_id, payload.magia_id)
