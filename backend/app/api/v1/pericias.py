"""
Router de Perícias
Single Responsibility: Apenas mapear endpoints HTTP
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.services.pericia_service import PericiaService
from app.schemas.pericia import (
    PericiaCreate, PericiaUpdate, PericiaResponse,
    PericiaJogadorCreate, PericiaJogadorUpdate, PericiaJogadorResponse,
    PericiaJogadorListResponse
)
from app.security import get_current_user

router = APIRouter(prefix="/api/v1/pericias", tags=["Perícias"])


# ========== ENDPOINTS DE PERÍCIAS DISPONÍVEIS ==========

@router.post("/", response_model=PericiaResponse, status_code=status.HTTP_201_CREATED)
def criar_pericia(
    pericia: PericiaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Cria uma nova perícia (Admin only)"""
    try:
        service = PericiaService(db)
        return service.criar_pericia(pericia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[PericiaResponse])
def listar_pericias(
    skip: int = 0,
    limit: int = 100,
    atributo: str = None,
    db: Session = Depends(get_db)
):
    """Lista todas as perícias disponíveis"""
    service = PericiaService(db)
    
    if atributo:
        return service.listar_pericias_por_atributo(atributo)
    
    return service.listar_todas_pericias(skip, limit)


@router.get("/{pericia_id}", response_model=PericiaResponse)
def obter_pericia(pericia_id: int, db: Session = Depends(get_db)):
    """Obtém uma perícia por ID"""
    service = PericiaService(db)
    pericia = service.obter_pericia(pericia_id)
    
    if not pericia:
        raise HTTPException(status_code=404, detail="Perícia não encontrada")
    
    return pericia


@router.put("/{pericia_id}", response_model=PericiaResponse)
def atualizar_pericia(
    pericia_id: int,
    pericia: PericiaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza uma perícia (Admin only)"""
    service = PericiaService(db)
    pericia_atualizada = service.atualizar_pericia(pericia_id, pericia)
    
    if not pericia_atualizada:
        raise HTTPException(status_code=404, detail="Perícia não encontrada")
    
    return pericia_atualizada


@router.delete("/{pericia_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pericia(
    pericia_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Deleta uma perícia (Admin only)"""
    service = PericiaService(db)
    
    if not service.deletar_pericia(pericia_id):
        raise HTTPException(status_code=404, detail="Perícia não encontrada")


# ========== ENDPOINTS DE PERÍCIAS DO JOGADOR ==========

@router.post("/{combatente_id}/adicionar", response_model=PericiaJogadorResponse, status_code=status.HTTP_201_CREATED)
def adicionar_pericia_jogador(
    combatente_id: int,
    pericia: PericiaJogadorCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Adiciona uma perícia ao jogador"""
    try:
        service = PericiaService(db)
        return service.adicionar_pericia_jogador(combatente_id, pericia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{combatente_id}/listar", response_model=PericiaJogadorListResponse)
def listar_pericias_jogador(
    combatente_id: int,
    db: Session = Depends(get_db)
):
    """Lista todas as perícias de um combatente"""
    service = PericiaService(db)
    stats = service.obter_estatisticas_pericias(combatente_id)
    
    return PericiaJogadorListResponse(
        pericias=stats["pericias"],
        total_pontos_gastos=stats["pontos_gastos"],
        pontos_disponiveis=stats["pontos_disponiveis"]
    )


@router.put("/{combatente_id}/pericia/{pericia_jogador_id}", response_model=PericiaJogadorResponse)
def atualizar_pericia_jogador(
    combatente_id: int,
    pericia_jogador_id: int,
    pericia: PericiaJogadorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Atualiza uma perícia do jogador"""
    service = PericiaService(db)
    pericia_atualizada = service.atualizar_pericia_jogador(pericia_jogador_id, pericia)
    
    if not pericia_atualizada:
        raise HTTPException(status_code=404, detail="Perícia do jogador não encontrada")
    
    return pericia_atualizada


@router.delete("/{combatente_id}/pericia/{pericia_jogador_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pericia_jogador(
    combatente_id: int,
    pericia_jogador_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Deleta uma perícia do jogador"""
    service = PericiaService(db)
    
    if not service.deletar_pericia_jogador(pericia_jogador_id):
        raise HTTPException(status_code=404, detail="Perícia do jogador não encontrada")


@router.get("/{combatente_id}/estatisticas")
def obter_estatisticas_pericias(
    combatente_id: int,
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de perícias do combatente"""
    service = PericiaService(db)
    return service.obter_estatisticas_pericias(combatente_id)