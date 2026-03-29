"""
Router de Equipamentos
Single Responsibility: Apenas mapear endpoints HTTP
SOLID: Dependency Injection via FastAPI
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import logging

# ✅ CORRETO: Import do core database
from app.core.database import get_db

# ✅ CORRETO: Import do service
from app.services.equipamento_service import EquipamentoService

# ✅ CORRETO: Import dos schemas
from app.schemas.equipamento import (
    EquipamentoCreate, EquipamentoResponse,
    EquipamentoJogadorCreate, EquipamentoJogadorListResponse
)

# ✅ CORRETO: Import do módulo de autenticação
from app.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/equipamentos", tags=["Equipamentos"])


# ========== ENDPOINTS DE EQUIPAMENTOS DISPONÍVEIS ==========

@router.post("/", response_model=EquipamentoResponse, status_code=status.HTTP_201_CREATED)
def criar_equipamento(
    equipamento: EquipamentoCreate,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual)
):
    """Cria um novo equipamento (Admin only)"""
    try:
        service = EquipamentoService(db)
        return service.criar_equipamento(equipamento)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar equipamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[EquipamentoResponse])
def listar_equipamentos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual)
):
    """Lista todos os equipamentos disponíveis"""
    try:
        service = EquipamentoService(db)
        return service.listar_todos_equipamentos(skip, limit)
    except Exception as e:
        logger.error(f"Erro ao listar equipamentos: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{equipamento_id}", response_model=EquipamentoResponse)
def obter_equipamento(
    equipamento_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(get_usuario_atual)
):
    """Obtém um equipamento específico"""
    try:
        service = EquipamentoService(db)
        equipamento = service.obter_equipamento(equipamento_id)
        
        if not equipamento:
            raise HTTPException(status_code=404, detail="Equipamento não encontrado")
        
        return equipamento
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter equipamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== ENDPOINTS DE EQUIPAMENTOS DO JOGADOR ==========

@router.post("/{combatente_id}/adicionar", response_model=EquipamentoJogadorListResponse, status_code=status.HTTP_201_CREATED)
def adicionar_equipamento_jogador(
    combatente_id: int,
    equipamento_jogador: EquipamentoJogadorCreate,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente)
):
    """Adiciona um equipamento ao combatente"""
    try:
        service = EquipamentoService(db)
        return service.adicionar_equipamento_jogador(combatente_id, equipamento_jogador)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar equipamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{combatente_id}/listar", response_model=List[EquipamentoJogadorListResponse])
def listar_equipamentos_jogador(
    combatente_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente)
):
    """Lista todos os equipamentos de um combatente"""
    try:
        service = EquipamentoService(db)
        return service.obter_equipamentos_jogador(combatente_id)
    except Exception as e:
        logger.error(f"Erro ao listar equipamentos do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{combatente_id}/remover/{equipamento_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover_equipamento_jogador(
    combatente_id: int,
    equipamento_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente)
):
    """Remove um equipamento do combatente"""
    try:
        service = EquipamentoService(db)
        
        if not service.remover_equipamento_jogador(combatente_id, equipamento_id):
            raise HTTPException(status_code=404, detail="Equipamento do jogador não encontrado")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao remover equipamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{combatente_id}/quantidade/{equipamento_id}")
def atualizar_quantidade_equipamento(
    combatente_id: int,
    equipamento_id: int,
    quantidade: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente)
):
    """Atualiza a quantidade de um equipamento"""
    try:
        service = EquipamentoService(db)
        result = service.atualizar_quantidade_equipamento(combatente_id, equipamento_id, quantidade)
        
        if not result and quantidade > 0:
            raise HTTPException(status_code=404, detail="Equipamento do jogador não encontrado")
        
        return {"mensagem": "Quantidade atualizada com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar quantidade: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
