"""
Router HTTP de Talentos (D&D 3.5)

Canônico em `app.games.dnd35.api.v1.talentos` (registrado em `app.main`).

NOTA: ainda **não** declara `requer_game_dnd35` (paridade com o original).
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.shared.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.games.dnd35.schemas.talento import (
    TalentoCreate,
    TalentoJogadorCreate,
    TalentoJogadorListResponse,
    TalentoResponse,
)
from app.games.dnd35.services.talento_service import TalentoService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/talentos", tags=["talentos"])


@router.post(
    "/", response_model=TalentoResponse, status_code=status.HTTP_201_CREATED
)
def criar_talento(
    talento: TalentoCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Cria um novo talento"""
    try:
        service = TalentoService(db)
        return service.criar_talento(talento)
    except Exception as e:
        logger.error(f"Erro ao criar talento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[TalentoResponse])
def listar_talentos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual),
):
    """Lista todos os talentos disponíveis"""
    try:
        service = TalentoService(db)
        return service.listar_talentos(skip, limit)
    except Exception as e:
        logger.error(f"Erro ao listar talentos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/{combatente_id}/adicionar", response_model=TalentoJogadorListResponse
)
def adicionar_talento_jogador(
    combatente_id: int,
    talento_jogador: TalentoJogadorCreate,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Adiciona um talento ao combatente"""
    try:
        service = TalentoService(db)
        return service.adicionar_talento_jogador(
            combatente_id, talento_jogador
        )
    except ValueError as e:
        logger.error(f"Validação falhou: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar talento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{combatente_id}/listar", response_model=List[TalentoJogadorListResponse]
)
def listar_talentos_jogador(
    combatente_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Lista todos os talentos de um combatente"""
    try:
        service = TalentoService(db)
        return service.obter_talentos_jogador(combatente_id)
    except Exception as e:
        logger.error(f"Erro ao listar talentos do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete(
    "/{combatente_id}/remover/{talento_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remover_talento_jogador(
    combatente_id: int,
    talento_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """Remove um talento do combatente"""
    try:
        service = TalentoService(db)

        if not service.remover_talento_jogador(combatente_id, talento_id):
            raise HTTPException(
                status_code=404, detail="Talento do jogador não encontrado"
            )

        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover talento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
