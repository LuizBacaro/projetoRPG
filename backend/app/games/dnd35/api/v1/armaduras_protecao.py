"""
Router de Armadura/Item de Proteção
SRP: mapear endpoints HTTP

Canônico em `app.games.dnd35.api.v1.armaduras_protecao` (registrado em `app.main`).
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_armadura_protecao_service
from app.games.dnd35.schemas.armadura_protecao import (
    ArmaduraProtecaoCreate,
    ArmaduraProtecaoJogadorCreate,
    ArmaduraProtecaoJogadorListResponse,
    ArmaduraProtecaoResponse,
    BonusCaResponse,
)
from app.games.dnd35.services.armadura_protecao_service import ArmaduraProtecaoService
from app.shared.core.deps import (
    get_usuario_atual,
    requer_dono_ou_admin_combatente,
    requer_game_dnd35,
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/armaduras_protecao",
    tags=["Armaduras/Proteção"],
    dependencies=[Depends(requer_game_dnd35)],
)


@router.post(
    "/", response_model=ArmaduraProtecaoResponse, status_code=status.HTTP_201_CREATED
)
def criar_item(
    payload: ArmaduraProtecaoCreate,
    service: ArmaduraProtecaoService = Depends(get_armadura_protecao_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        return service.criar_item(payload)
    except Exception as exc:
        logger.error("Erro ao criar item de proteção: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/", response_model=List[ArmaduraProtecaoResponse])
def listar_itens(
    skip: int = 0,
    limit: int = 100,
    service: ArmaduraProtecaoService = Depends(get_armadura_protecao_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        return service.listar_itens(skip, limit)
    except Exception as exc:
        logger.error("Erro ao listar itens de proteção: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/item/{item_id}", response_model=ArmaduraProtecaoResponse)
def obter_item(
    item_id: int,
    service: ArmaduraProtecaoService = Depends(get_armadura_protecao_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        item = service.obter_item(item_id)
        if not item:
            raise HTTPException(
                status_code=404, detail="Item de proteção não encontrado"
            )
        return item
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Erro ao obter item de proteção: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post(
    "/{combatente_id}/adicionar",
    response_model=ArmaduraProtecaoJogadorListResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_item_jogador(
    combatente_id: int,
    payload: ArmaduraProtecaoJogadorCreate,
    service: ArmaduraProtecaoService = Depends(get_armadura_protecao_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.adicionar_item_jogador(combatente_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Erro ao adicionar item de proteção: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get(
    "/{combatente_id}/listar", response_model=List[ArmaduraProtecaoJogadorListResponse]
)
def listar_itens_jogador(
    combatente_id: int,
    service: ArmaduraProtecaoService = Depends(get_armadura_protecao_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.listar_itens_jogador(combatente_id)
    except Exception as exc:
        logger.error("Erro ao listar itens de proteção do jogador: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete(
    "/{combatente_id}/remover/{item_id}", status_code=status.HTTP_204_NO_CONTENT
)
def remover_item_jogador(
    combatente_id: int,
    item_id: int,
    service: ArmaduraProtecaoService = Depends(get_armadura_protecao_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        removido = service.remover_item_jogador(combatente_id, item_id)
        if not removido:
            raise HTTPException(
                status_code=404, detail="Item de proteção do jogador não encontrado"
            )
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Erro ao remover item de proteção do jogador: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{combatente_id}/bonus-ca", response_model=BonusCaResponse)
def obter_bonus_ca_total(
    combatente_id: int,
    service: ArmaduraProtecaoService = Depends(get_armadura_protecao_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return BonusCaResponse(bonus_ca_total=service.bonus_ca_total(combatente_id))
    except Exception as exc:
        logger.error("Erro ao calcular bônus total de CA: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
