"""
Router de Armadura/Item de Proteção
SRP: mapear endpoints HTTP
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import (
    get_usuario_atual,
    requer_dono_ou_admin_combatente,
    requer_game_dnd35,
)
from app.schemas.armadura_protecao import (
    ArmaduraProtecaoCreate,
    ArmaduraProtecaoJogadorCreate,
    ArmaduraProtecaoJogadorListResponse,
    ArmaduraProtecaoResponse,
    BonusCaResponse,
)
from app.services.armadura_protecao_service import ArmaduraProtecaoService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/armaduras_protecao",
    tags=["Armaduras/Proteção"],
    dependencies=[Depends(requer_game_dnd35)],
)


@router.post("/", response_model=ArmaduraProtecaoResponse, status_code=status.HTTP_201_CREATED)
def criar_item(
    payload: ArmaduraProtecaoCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    try:
        service = ArmaduraProtecaoService(db)
        return service.criar_item(payload)
    except Exception as exc:
        logger.error("Erro ao criar item de proteção: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/", response_model=List[ArmaduraProtecaoResponse])
def listar_itens(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    try:
        service = ArmaduraProtecaoService(db)
        return service.listar_itens(skip, limit)
    except Exception as exc:
        logger.error("Erro ao listar itens de proteção: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/item/{item_id}", response_model=ArmaduraProtecaoResponse)
def obter_item(
    item_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    try:
        service = ArmaduraProtecaoService(db)
        item = service.obter_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item de proteção não encontrado")
        return item
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Erro ao obter item de proteção: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/{combatente_id}/adicionar", response_model=ArmaduraProtecaoJogadorListResponse, status_code=status.HTTP_201_CREATED)
def adicionar_item_jogador(
    combatente_id: int,
    payload: ArmaduraProtecaoJogadorCreate,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        service = ArmaduraProtecaoService(db)
        return service.adicionar_item_jogador(combatente_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        logger.error("Erro ao adicionar item de proteção: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{combatente_id}/listar", response_model=List[ArmaduraProtecaoJogadorListResponse])
def listar_itens_jogador(
    combatente_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        service = ArmaduraProtecaoService(db)
        return service.listar_itens_jogador(combatente_id)
    except Exception as exc:
        logger.error("Erro ao listar itens de proteção do jogador: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.delete("/{combatente_id}/remover/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_item_jogador(
    combatente_id: int,
    item_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        service = ArmaduraProtecaoService(db)
        removido = service.remover_item_jogador(combatente_id, item_id)
        if not removido:
            raise HTTPException(status_code=404, detail="Item de proteção do jogador não encontrado")
        return None
    except HTTPException:
        raise
    except Exception as exc:
        logger.error("Erro ao remover item de proteção do jogador: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{combatente_id}/bonus-ca", response_model=BonusCaResponse)
def obter_bonus_ca_total(
    combatente_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        service = ArmaduraProtecaoService(db)
        return BonusCaResponse(bonus_ca_total=service.bonus_ca_total(combatente_id))
    except Exception as exc:
        logger.error("Erro ao calcular bônus total de CA: %s", exc)
        raise HTTPException(status_code=500, detail=str(exc))
