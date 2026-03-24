"""
api/v1/talentos.py
SRP: Rotas HTTP para gerenciamento de talentos
SOLID: Controllers thin, lógica no Service
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.talento_service import TalentoService
from app.schemas.talento import TalentoCreate, TalentoJogadorCreate, TalentoJogadorListResponse, TalentoResponse
from typing import List
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/talentos", tags=["talentos"])


@router.post("/", response_model=TalentoResponse, status_code=status.HTTP_201_CREATED)
def criar_talento(
    talento: TalentoCreate,
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
):
    """Lista todos os talentos disponíveis"""
    try:
        service = TalentoService(db)
        return service.listar_talentos(skip, limit)
    except Exception as e:
        logger.error(f"Erro ao listar talentos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{combatente_id}/adicionar", response_model=TalentoJogadorListResponse)
def adicionar_talento_jogador(
    combatente_id: int,
    talento_jogador: TalentoJogadorCreate,
    db: Session = Depends(get_db)
):
    """Adiciona um talento ao combatente"""
    try:
        service = TalentoService(db)
        return service.adicionar_talento_jogador(combatente_id, talento_jogador)
    except ValueError as e:
        logger.error(f"Validação falhou: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar talento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{combatente_id}/listar", response_model=List[TalentoJogadorListResponse])
def listar_talentos_jogador(
    combatente_id: int,
    db: Session = Depends(get_db)
):
    """Lista todos os talentos de um combatente"""
    try:
        service = TalentoService(db)
        return service.obter_talentos_jogador(combatente_id)
    except Exception as e:
        logger.error(f"Erro ao listar talentos do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{combatente_id}/remover/{talento_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_talento_jogador(
    combatente_id: int,
    talento_id: int,
    db: Session = Depends(get_db)
):
    """Remove um talento do combatente"""
    try:
        service = TalentoService(db)
        
        if not service.remover_talento_jogador(combatente_id, talento_id):
            raise HTTPException(status_code=404, detail="Talento do jogador não encontrado")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover talento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
