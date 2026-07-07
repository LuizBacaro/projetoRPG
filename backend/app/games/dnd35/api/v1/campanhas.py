"""
Router de Campanhas (D&D 3.5)
SRP: apenas mapear endpoints HTTP do domínio "campanhas".

Canônico em `app.games.dnd35.api.v1.campanhas` (registrado em `app.main`).

Já declara o guard `requer_game_dnd35` (paridade com o original).
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.core.dependencies import get_campanha_service, get_sessao_campanha_service
from app.games.dnd35.schemas.campanha import (
    CampanhaCreate,
    CampanhaResponse,
    CampanhaUpdate,
)
from app.games.dnd35.schemas.sessao_campanha import (
    SessaoCampanhaCreate,
    SessaoCampanhaResponse,
    SessaoCampanhaUpdate,
)
from app.games.dnd35.services.campanha_service import CampanhaService
from app.games.dnd35.services.sessao_campanha_service import SessaoCampanhaService
from app.shared.core.deps import get_usuario_atual, requer_game_dnd35
from app.shared.exceptions.custom_exceptions import ArenaBaseException

router = APIRouter(
    prefix="/campanhas",
    tags=["Campanhas"],
    dependencies=[Depends(requer_game_dnd35)],
)


@router.get("", response_model=list[CampanhaResponse])
def listar_campanhas(
    service: CampanhaService = Depends(get_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    return service.listar_por_mestre(usuario.id)


@router.post("", response_model=CampanhaResponse, status_code=status.HTTP_201_CREATED)
def criar_campanha(
    payload: CampanhaCreate,
    service: CampanhaService = Depends(get_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        return service.criar(
            mestre_id=usuario.id,
            nome=payload.nome,
            descricao=payload.descricao or "",
            personagem_ids=payload.personagem_ids,
        )
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.put("/{campanha_id}", response_model=CampanhaResponse)
def atualizar_campanha(
    campanha_id: int,
    payload: CampanhaUpdate,
    service: CampanhaService = Depends(get_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        return service.atualizar(
            campanha_id=campanha_id,
            mestre_id=usuario.id,
            nome=payload.nome,
            descricao=payload.descricao,
            personagem_ids=payload.personagem_ids,
        )
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post("/{campanha_id}/personagens", response_model=CampanhaResponse)
def associar_personagens(
    campanha_id: int,
    personagem_ids: list[int],
    service: CampanhaService = Depends(get_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        return service.associar_personagens(campanha_id, usuario.id, personagem_ids)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{campanha_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_campanha(
    campanha_id: int,
    service: CampanhaService = Depends(get_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        service.deletar(campanha_id, usuario.id)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return None


@router.get("/sessoes", response_model=list[SessaoCampanhaResponse])
def listar_sessoes_campanha(
    service: SessaoCampanhaService = Depends(get_sessao_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    return service.listar_por_mestre(usuario.id)


@router.post(
    "/sessoes",
    response_model=SessaoCampanhaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_sessao_campanha(
    payload: SessaoCampanhaCreate,
    service: SessaoCampanhaService = Depends(get_sessao_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        return service.criar(
            mestre_id=usuario.id,
            campanha_id=payload.campanha_id,
            resumo=payload.resumo,
            visivel_jogadores=payload.visivel_jogadores,
        )
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.put("/sessoes/{sessao_id}", response_model=SessaoCampanhaResponse)
def atualizar_sessao_campanha(
    sessao_id: int,
    payload: SessaoCampanhaUpdate,
    service: SessaoCampanhaService = Depends(get_sessao_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        return service.atualizar(
            mestre_id=usuario.id,
            sessao_id=sessao_id,
            resumo=payload.resumo,
            visivel_jogadores=payload.visivel_jogadores,
        )
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/sessoes/{sessao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_sessao_campanha(
    sessao_id: int,
    service: SessaoCampanhaService = Depends(get_sessao_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        service.deletar(usuario.id, sessao_id)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return None
