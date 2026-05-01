"""HTTP — campanhas GURPS."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_gurps_campanha_service
from app.games.gurps.schemas.campanha import (
    GurpsCampanhaCreate,
    GurpsCampanhaResponse,
    GurpsCampanhaUpdate,
)
from app.games.gurps.services.campanha_service import GurpsCampanhaService
from app.shared.core.deps import requer_game_gurps, requer_mestre_ou_admin
from app.shared.exceptions.custom_exceptions import ArenaBaseException

router = APIRouter(
    prefix="/gurps/campanhas",
    tags=["GURPS — Campanhas"],
    dependencies=[Depends(requer_game_gurps)],
)


@router.get("", response_model=list[GurpsCampanhaResponse])
def listar(
    service: GurpsCampanhaService = Depends(get_gurps_campanha_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    rows = service.listar_por_mestre(usuario.id)
    return [GurpsCampanhaResponse.model_validate(c) for c in rows]


@router.post("", response_model=GurpsCampanhaResponse, status_code=status.HTTP_201_CREATED)
def criar(
    payload: GurpsCampanhaCreate,
    service: GurpsCampanhaService = Depends(get_gurps_campanha_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    try:
        c = service.criar(
            mestre_id=usuario.id,
            nome=payload.nome,
            descricao=payload.descricao or "",
            personagem_ids=payload.personagem_ids,
        )
        return GurpsCampanhaResponse.model_validate(c)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.put("/{campanha_id}", response_model=GurpsCampanhaResponse)
def atualizar(
    campanha_id: int,
    payload: GurpsCampanhaUpdate,
    service: GurpsCampanhaService = Depends(get_gurps_campanha_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    try:
        c = service.atualizar(
            campanha_id=campanha_id,
            mestre_id=usuario.id,
            nome=payload.nome,
            descricao=payload.descricao,
            personagem_ids=payload.personagem_ids,
        )
        return GurpsCampanhaResponse.model_validate(c)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{campanha_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(
    campanha_id: int,
    service: GurpsCampanhaService = Depends(get_gurps_campanha_service),
    usuario=Depends(requer_mestre_ou_admin),
):
    try:
        service.deletar(campanha_id, usuario.id)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
