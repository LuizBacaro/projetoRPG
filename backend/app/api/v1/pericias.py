"""
Router de Perícias
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
from app.services.pericia_service import PericiaService

# ✅ CORRETO: Import dos schemas
from app.schemas.pericia import (
    PericiaCreate, PericiaUpdate, PericiaResponse,
    PericiaJogadorCreate, PericiaJogadorUpdate, PericiaJogadorResponse,
    PericiaJogadorListResponse
)

# ✅ CORRETO: Busque o módulo de segurança (pode estar em outro lugar)
# Tente importar de onde realmente está em seu projeto
try:
    # Opção 1: Se estiver em app/core/security.py
    from app.core.security import get_current_user
except ImportError:
    try:
        # Opção 2: Se estiver em app/security.py
        from app.security import get_current_user
    except ImportError:
        # Opção 3: Se não existir, criar um dummy (sem autenticação)
        async def get_current_user(request=None):
            return None

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pericias", tags=["Perícias"])


# ========== ENDPOINTS DE PERÍCIAS DISPONÍVEIS ==========

@router.post("/", response_model=PericiaResponse, status_code=status.HTTP_201_CREATED)
def criar_pericia(
    pericia: PericiaCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) if get_current_user else None
):
    """Cria uma nova perícia (Admin only)"""
    try:
        service = PericiaService(db)
        return service.criar_pericia(pericia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao criar perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[PericiaResponse])
def listar_pericias(
    skip: int = 0,
    limit: int = 100,
    atributo: str = None,
    classe: str = None,
    db: Session = Depends(get_db)
):
    """Lista todas as perícias disponíveis com custo baseado em classe"""
    try:
        service = PericiaService(db)
        
        if atributo:
            pericias = service.listar_pericias_por_atributo(atributo)
        else:
            pericias = service.listar_todas_pericias(skip, limit)
        
        # Se classe foi especificada, calcula custo para cada perícia
        if classe:
            pericias_com_custo = []
            for pericia in pericias:
                custo = service.calcular_custo_pericia(pericia.id, classe)
                pericia.custo_para_classe = custo
                pericias_com_custo.append(pericia)
            return pericias_com_custo
        
        return pericias
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao listar perícias: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{pericia_id}", response_model=PericiaResponse)
def obter_pericia(
    pericia_id: int,
    classe: str = None,
    db: Session = Depends(get_db)
):
    """Obtém uma perícia por ID com custo baseado em classe se fornecido"""
    try:
        service = PericiaService(db)
        pericia = service.obter_pericia(pericia_id)
        
        if not pericia:
            raise HTTPException(status_code=404, detail="Perícia não encontrada")
        
        # Se classe foi especificada, calcula custo
        if classe:
            custo = service.calcular_custo_pericia(pericia_id, classe)
            pericia.custo_para_classe = custo
        
        return pericia
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{pericia_id}", response_model=PericiaResponse)
def atualizar_pericia(
    pericia_id: int,
    pericia: PericiaUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) if get_current_user else None
):
    """Atualiza uma perícia (Admin only)"""
    try:
        service = PericiaService(db)
        pericia_atualizada = service.atualizar_pericia(pericia_id, pericia)
        
        if not pericia_atualizada:
            raise HTTPException(status_code=404, detail="Perícia não encontrada")
        
        return pericia_atualizada
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/classe/{classe_nome}", response_model=List[PericiaResponse])
def listar_pericias_classe(
    classe_nome: str,
    db: Session = Depends(get_db)
):
    """Lista perícias padrão de uma classe com seus custos"""
    try:
        service = PericiaService(db)
        pericias = service.listar_pericias_por_classe(classe_nome)
        
        # Calcula custo para cada perícia
        pericias_com_custo = []
        for pericia in pericias:
            custo = service.calcular_custo_pericia(pericia.id, classe_nome)
            pericia.custo_para_classe = custo
            pericias_com_custo.append(pericia)
        
        return pericias_com_custo
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao listar perícias da classe: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{pericia_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pericia(
    pericia_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) if get_current_user else None
):
    """Deleta uma perícia (Admin only)"""
    try:
        service = PericiaService(db)
        
        if not service.deletar_pericia(pericia_id):
            raise HTTPException(status_code=404, detail="Perícia não encontrada")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# ========== ENDPOINTS DE PERÍCIAS DO JOGADOR ==========

@router.post("/{combatente_id}/adicionar", response_model=PericiaJogadorResponse, status_code=status.HTTP_201_CREATED)
def adicionar_pericia_jogador(
    combatente_id: int,
    pericia: PericiaJogadorCreate,
    classe: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) if get_current_user else None
):
    """Adiciona uma perícia ao jogador com validação de custo"""
    try:
        service = PericiaService(db)
        
        # Se classe foi fornecida, calcula e valida o custo
        if classe:
            custo_unitario = service.calcular_custo_pericia(pericia.pericia_id, classe)
            custo_total = service.calcular_custo_total_graduacao(
                pericia.pericia_id, 
                classe, 
                pericia.graduacao
            )
            
            # Obtém o combatente para validar pontos disponíveis
            combatente = service.repository.obter_combatente(combatente_id)
            if not combatente:
                raise ValueError(f"Combatente {combatente_id} não encontrado")
            
            pontos_disponiveis = combatente.pontos_pericia
            if custo_total > pontos_disponiveis:
                raise ValueError(
                    f"Pontos insuficientes. Necessário: {custo_total}, "
                    f"Disponível: {pontos_disponiveis}"
                )
        
        return service.adicionar_pericia_jogador(combatente_id, pericia)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro ao adicionar perícia: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{combatente_id}/listar", response_model=PericiaJogadorListResponse)
def listar_pericias_jogador(
    combatente_id: int,
    db: Session = Depends(get_db)
):
    """Lista todas as perícias de um combatente"""
    try:
        service = PericiaService(db)
        stats = service.obter_estatisticas_pericias(combatente_id)
        
        return PericiaJogadorListResponse(
            pericias=stats["pericias"],
            total_pontos_gastos=stats["pontos_gastos_total"],
            pontos_disponiveis=stats["pontos_disponiveis"]
        )
    except Exception as e:
        logger.error(f"Erro ao listar perícias do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{combatente_id}/pericia/{pericia_jogador_id}", response_model=PericiaJogadorResponse)
def atualizar_pericia_jogador(
    combatente_id: int,
    pericia_jogador_id: int,
    pericia: PericiaJogadorUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) if get_current_user else None
):
    """Atualiza uma perícia do jogador"""
    try:
        service = PericiaService(db)
        pericia_atualizada = service.atualizar_pericia_jogador(pericia_jogador_id, pericia)
        
        if not pericia_atualizada:
            raise HTTPException(status_code=404, detail="Perícia do jogador não encontrada")
        
        return pericia_atualizada
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao atualizar perícia do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{combatente_id}/pericia/{pericia_jogador_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_pericia_jogador(
    combatente_id: int,
    pericia_jogador_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user) if get_current_user else None
):
    """Deleta uma perícia do jogador"""
    try:
        service = PericiaService(db)
        
        if not service.deletar_pericia_jogador(pericia_jogador_id):
            raise HTTPException(status_code=404, detail="Perícia do jogador não encontrada")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao deletar perícia do jogador: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{combatente_id}/estatisticas")
def obter_estatisticas_pericias(
    combatente_id: int,
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de perícias do combatente"""
    try:
        service = PericiaService(db)
        return service.obter_estatisticas_pericias(combatente_id)
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))