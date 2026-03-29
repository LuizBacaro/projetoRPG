"""
Router de Condições
Princípio SOLID: SRP - Apenas HTTP routing de Condição
DIP - Depende de get_condicao_service (abstração)
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ...core.database import get_db
from ...core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from ...core.dependencies import get_condicao_service, get_combate_service
from ...schemas.condicao import (
    CondicaoResponse,
    AplicarCondicaoRequest,
    RemoverCondicaoRequest,
    CondicaoAtivaResponse,
)
from ...exceptions.custom_exceptions import ArenaBaseException

router = APIRouter(prefix="/condicoes", tags=["Condições"])


# ── Catálogo ────────────────────────────────────────────────────────────────────

@router.get("", response_model=List[CondicaoResponse])
def listar_condicoes(db: Session = Depends(get_db), _: object = Depends(get_usuario_atual)):
    """
    ✅ Retorna todas as 25 condições D&D disponíveis
    """
    service = get_condicao_service(db)
    return service.listar_todas()


# ── Por combatente ───────────────────────────────────────────────────────────────

@router.get("/combatente/{combatente_id}", response_model=CondicaoAtivaResponse)
def listar_condicoes_combatente(combatente_id: int, db: Session = Depends(get_db), _: object = Depends(requer_dono_ou_admin_combatente)):
    """
    ✅ Lista condições ativas de um combatente
    Retorna: {combatente_id, condicoes: []}
    """
    service = get_condicao_service(db)
    try:
        return service.listar_condicoes_do_combatente(combatente_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/combatente/{combatente_id}", response_model=CondicaoAtivaResponse)
def aplicar_condicao(
    combatente_id: int,
    body: AplicarCondicaoRequest,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    ✅ Aplica uma condição a um combatente
    Body: {condicao_id, duracao_turnos (opcional, default -1)}
    """
    service = get_condicao_service(db)
    try:
        # ✅ Passar duração se fornecida, senão default -1 (permanente)
        duracao = getattr(body, 'duracao_turnos', -1) or -1
        return service.aplicar_condicao(combatente_id, body.condicao_id, duracao)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/combatente/{combatente_id}/{condicao_id}", response_model=CondicaoAtivaResponse)
def remover_condicao(
    combatente_id: int,
    condicao_id: int,
    db: Session = Depends(get_db),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    ✅ Remove uma condição específica de um combatente
    """
    service = get_condicao_service(db)
    try:
        return service.remover_condicao(combatente_id, condicao_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/combatente/{combatente_id}", response_model=CondicaoAtivaResponse)
def remover_todas_condicoes(combatente_id: int, db: Session = Depends(get_db), _: object = Depends(requer_dono_ou_admin_combatente)):
    """
    ✅ Remove todas as condições ativas de um combatente
    """
    service = get_condicao_service(db)
    try:
        return service.remover_todas_condicoes(combatente_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/combatentes/{combatente_id}/avancar-turno")
def avancar_turno_condicoes(combatente_id: int, db: Session = Depends(get_db), _: object = Depends(requer_dono_ou_admin_combatente)):
    """
    ✅ NOVO: Decrementa duração de TODAS as condições do combatente em 1 turno.
    Remove automaticamente condições que expirarem (duracao_turnos = 0).
    
    Chamado automaticamente por ArenaController.avancarTurno()
    
    Response:
    {
        "combatente_id": int,
        "condicoes": [
            {
                "id": int,
                "condicao_id": int,
                "nome": str,
                "efeito": str,
                "duracao_turnos": int (-1 = permanente)
            }
        ]
    }
    """
    service = get_condicao_service(db)
    try:
        result = service.decrementar_duracao_todas(combatente_id)
        return result
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        print(f"❌ Erro inesperado ao decrementar duração: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")