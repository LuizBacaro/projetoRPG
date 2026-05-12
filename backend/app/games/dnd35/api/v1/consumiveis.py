import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_consumivel_service
from app.games.dnd35.schemas.consumivel import (
    ConsumivelCreate,
    ConsumivelJogadorCreate,
    ConsumivelJogadorListResponse,
    ConsumivelResponse,
)
from app.games.dnd35.services.consumivel_service import ConsumivelService
from app.shared.core.deps import (
    get_usuario_atual,
    requer_admin,
    requer_dono_ou_admin_combatente,
)
from app.shared.exceptions.custom_exceptions import CombatenteNaoEncontrado

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/consumiveis", tags=["Consumiveis"])


@router.post(
    "/", response_model=ConsumivelResponse, status_code=status.HTTP_201_CREATED
)
def criar_consumivel(
    payload: ConsumivelCreate,
    service: ConsumivelService = Depends(get_consumivel_service),
    _: object = Depends(get_usuario_atual),
):
    try:
        return service.criar(payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ConsumivelResponse])
def listar_consumiveis(
    skip: int = 0,
    limit: int = 100,
    tipo: str | None = None,
    categoria: str | None = None,
    busca: str | None = None,
    service: ConsumivelService = Depends(get_consumivel_service),
    _: object = Depends(get_usuario_atual),
):
    return service.listar(
        skip,
        limit,
        tipo=tipo,
        categoria=categoria,
        busca=busca,
    )


@router.get("/{consumivel_id}", response_model=ConsumivelResponse)
def obter_consumivel(
    consumivel_id: int,
    service: ConsumivelService = Depends(get_consumivel_service),
    _: object = Depends(get_usuario_atual),
):
    item = service.obter(consumivel_id)
    if not item:
        raise HTTPException(status_code=404, detail="Consumível não encontrado")
    return item


@router.delete("/catalogo/{consumivel_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_consumivel_catalogo(
    consumivel_id: int,
    service: ConsumivelService = Depends(get_consumivel_service),
    _: object = Depends(requer_admin),
):
    if not service.deletar(consumivel_id):
        raise HTTPException(status_code=404, detail="Consumível não encontrado")
    return None


@router.post(
    "/{combatente_id}/adicionar",
    response_model=ConsumivelJogadorListResponse,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_consumivel_jogador(
    combatente_id: int,
    payload: ConsumivelJogadorCreate,
    service: ConsumivelService = Depends(get_consumivel_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.adicionar_jogador(combatente_id, payload)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/{combatente_id}/listar",
    response_model=List[ConsumivelJogadorListResponse],
)
def listar_consumiveis_jogador(
    combatente_id: int,
    service: ConsumivelService = Depends(get_consumivel_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        return service.listar_jogador(combatente_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete(
    "/{combatente_id}/remover/{consumivel_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remover_consumivel_jogador(
    combatente_id: int,
    consumivel_id: int,
    service: ConsumivelService = Depends(get_consumivel_service),
    _: object = Depends(requer_dono_ou_admin_combatente),
):
    try:
        ok = service.remover_jogador(combatente_id, consumivel_id)
    except CombatenteNaoEncontrado as e:
        raise HTTPException(status_code=404, detail=str(e))
    if not ok:
        raise HTTPException(
            status_code=404, detail="Consumível do jogador não encontrado"
        )
    return None
