"""
Router de Condições
Princípio SOLID: SRP - Apenas HTTP routing de Condição
DIP - Depende de get_condicao_service (abstração)

Implementação em `app.games.dnd35.api.v1.condicoes`; shim em
`app.api.v1.condicoes` durante a reorganização multi-jogo.
"""
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_condicao_service
from app.core.deps import get_usuario_atual, requer_dono_ou_admin_combatente
from app.exceptions.custom_exceptions import ArenaBaseException
from app.games.dnd35.schemas.condicao import (
    AplicarCondicaoMassaRequest,
    AplicarCondicaoMassaResponse,
    AplicarCondicaoRequest,
    CondicaoAtivaResponse,
    CondicaoResponse,
)
from app.games.dnd35.services.condicao_service import CondicaoService

router = APIRouter(prefix="/condicoes", tags=["Condições"])


# ── Catálogo ────────────────────────────────────────────────────────────────────


@router.get("", response_model=List[CondicaoResponse])
def listar_condicoes(
    service: CondicaoService = Depends(get_condicao_service),
    _: object = Depends(get_usuario_atual),
):
    """
    ✅ Retorna todas as 25 condições D&D disponíveis
    """
    return service.listar_todas()


# ── Por combatente ───────────────────────────────────────────────────────────────


@router.get("/combatente/{combatente_id}", response_model=CondicaoAtivaResponse)
def listar_condicoes_combatente(
    combatente_id: int,
    service: CondicaoService = Depends(get_condicao_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    ✅ Lista condições ativas de um combatente
    Retorna: {combatente_id, condicoes: []}
    """
    try:
        return service.listar_condicoes_do_combatente(combatente_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/combatente/{combatente_id}", response_model=CondicaoAtivaResponse)
def aplicar_condicao(
    combatente_id: int,
    body: AplicarCondicaoRequest,
    service: CondicaoService = Depends(get_condicao_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    ✅ Aplica uma condição a um combatente
    Body: {condicao_id, duracao_turnos (opcional, default -1)}
    """
    try:
        # ✅ Passar duração se fornecida, senão default -1 (permanente)
        duracao = getattr(body, "duracao_turnos", -1) or -1
        return service.aplicar_condicao(combatente_id, body.condicao_id, duracao)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/combatentes/aplicar", response_model=AplicarCondicaoMassaResponse)
def aplicar_condicao_combatentes(
    body: AplicarCondicaoMassaRequest,
    service: CondicaoService = Depends(get_condicao_service),
    usuario_atual: object = Depends(get_usuario_atual),
):
    """Aplica uma condição para múltiplos combatentes em lote."""
    try:
        return service.aplicar_condicao_em_lote(
            body.combatente_ids,
            body.condicao_id,
            body.duracao_turnos,
            usuario_atual,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/combatente/{combatente_id}/{condicao_id}", response_model=CondicaoAtivaResponse)
def remover_condicao(
    combatente_id: int,
    condicao_id: int,
    service: CondicaoService = Depends(get_condicao_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    ✅ Remove uma condição específica de um combatente
    """
    try:
        return service.remover_condicao(combatente_id, condicao_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.delete("/combatente/{combatente_id}", response_model=CondicaoAtivaResponse)
def remover_todas_condicoes(
    combatente_id: int,
    service: CondicaoService = Depends(get_condicao_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    """
    ✅ Remove todas as condições ativas de um combatente
    """
    try:
        return service.remover_todas_condicoes(combatente_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/combatentes/{combatente_id}/avancar-turno")
def avancar_turno_condicoes(
    combatente_id: int,
    service: CondicaoService = Depends(get_condicao_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
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
    try:
        result = service.decrementar_duracao_todas(combatente_id)
        return result
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except Exception as e:
        print(f"❌ Erro inesperado ao decrementar duração: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")
