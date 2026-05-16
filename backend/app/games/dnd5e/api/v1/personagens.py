"""HTTP — personagens D&D 5e."""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile

from app.core.dependencies import get_dnd5e_personagem_service, get_file_service
from app.games.dnd5e.schemas.personagem import (
    Dnd5ePersonagemCreate,
    Dnd5ePersonagemResponse,
    Dnd5ePersonagemUpdate,
)
from app.games.dnd5e.services.personagem_service import Dnd5ePersonagemService
from app.services.file_service import FileService
from app.shared.core.deps import (
    get_usuario_atual,
    requer_dono_ou_admin_dnd5e_personagem,
    requer_game_dnd5e,
)
from app.shared.exceptions.custom_exceptions import (
    ArenaBaseException,
    DadosInvalidos,
    InvalidFileError,
)
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/dnd5e/personagens",
    tags=["D&D 5e — Personagens"],
    dependencies=[Depends(requer_game_dnd5e)],
)


@router.get("", response_model=List[Dnd5ePersonagemResponse])
def listar(
    tipo: Optional[str] = None,
    meus: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    response: Response = None,
    service: Dnd5ePersonagemService = Depends(get_dnd5e_personagem_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    total = service.contar_todos(tipo, usuario=usuario_atual, apenas_meus=meus)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)
    return service.listar_todos(
        tipo,
        usuario=usuario_atual,
        skip=skip,
        limit=limit,
        apenas_meus=meus,
    )


@router.get("/{personagem_id}", response_model=Dnd5ePersonagemResponse)
def obter(
    personagem_id: int,
    service: Dnd5ePersonagemService = Depends(get_dnd5e_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        return service.obter_resposta(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("", response_model=Dnd5ePersonagemResponse, status_code=201)
def criar(
    payload: Dnd5ePersonagemCreate,
    service: Dnd5ePersonagemService = Depends(get_dnd5e_personagem_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        return service.criar(usuario_atual, payload)
    except (ArenaBaseException, DadosInvalidos) as e:
        code = getattr(e, "status_code", 422)
        raise HTTPException(status_code=code, detail=getattr(e, "message", str(e)))


@router.patch("/{personagem_id}", response_model=Dnd5ePersonagemResponse)
def atualizar(
    personagem_id: int,
    payload: Dnd5ePersonagemUpdate,
    service: Dnd5ePersonagemService = Depends(get_dnd5e_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        return service.atualizar(personagem_id, payload)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{personagem_id}/foto", response_model=Dnd5ePersonagemResponse)
def upload_foto(
    personagem_id: int,
    foto: UploadFile = File(...),
    service: Dnd5ePersonagemService = Depends(get_dnd5e_personagem_service),
    file_service: FileService = Depends(get_file_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    if not foto.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")
    try:
        ent = service.obter_por_id(personagem_id)
        if ent.foto_url:
            file_service.deletar_arquivo(ent.foto_url)
        url = file_service.salvar_arquivo(foto)
        return service.atualizar(
            personagem_id, Dnd5ePersonagemUpdate(foto_url=url)
        )
    except InvalidFileError as e:
        raise HTTPException(status_code=400, detail=e.message)
