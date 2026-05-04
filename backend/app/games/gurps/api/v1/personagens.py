"""HTTP — personagens GURPS (equivalente a combatentes na UI)."""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile

from app.core.dependencies import get_file_service, get_gurps_personagem_service
from app.games.gurps.schemas.personagem import (
    GurpsPersonagemCreate,
    GurpsPersonagemResponse,
    GurpsPersonagemUpdate,
)
from app.games.gurps.services.personagem_service import GurpsPersonagemService
from app.shared.core.deps import (
    get_usuario_atual,
    requer_dono_ou_admin_gurps_personagem,
    requer_game_gurps,
)
from app.services.file_service import FileService
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos, InvalidFileError
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/gurps/personagens",
    tags=["GURPS — Personagens"],
    dependencies=[Depends(requer_game_gurps)],
)


@router.get("", response_model=List[GurpsPersonagemResponse])
def listar(
    tipo: Optional[str] = None,
    meus: bool = Query(False),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    response: Response = None,
    service: GurpsPersonagemService = Depends(get_gurps_personagem_service),
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


@router.get("/catalogo/pericias-lite")
def catalogo_pericias_lite(
    service: GurpsPersonagemService = Depends(get_gurps_personagem_service),
    _: Usuario = Depends(get_usuario_atual),
):
    return {"itens": service.catalogo_pericias_lite()}


@router.get("/{personagem_id}", response_model=GurpsPersonagemResponse)
def obter(
    personagem_id: int,
    service: GurpsPersonagemService = Depends(get_gurps_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_gurps_personagem),
):
    try:
        ent = service.obter_por_id(personagem_id)
        return GurpsPersonagemResponse.model_validate(ent)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("", response_model=GurpsPersonagemResponse, status_code=201)
def criar(
    payload: GurpsPersonagemCreate,
    service: GurpsPersonagemService = Depends(get_gurps_personagem_service),
    usuario_atual: Usuario = Depends(get_usuario_atual),
):
    try:
        return service.criar(usuario_atual, payload)
    except (ArenaBaseException, DadosInvalidos) as e:
        code = getattr(e, "status_code", 422)
        raise HTTPException(status_code=code, detail=getattr(e, "message", str(e)))


@router.patch("/{personagem_id}", response_model=GurpsPersonagemResponse)
def atualizar(
    personagem_id: int,
    payload: GurpsPersonagemUpdate,
    service: GurpsPersonagemService = Depends(get_gurps_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_gurps_personagem),
):
    try:
        return service.atualizar(personagem_id, payload)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/{personagem_id}/foto", response_model=GurpsPersonagemResponse)
def upload_foto(
    personagem_id: int,
    foto: UploadFile = File(...),
    service: GurpsPersonagemService = Depends(get_gurps_personagem_service),
    file_service: FileService = Depends(get_file_service),
    _: Usuario = Depends(requer_dono_ou_admin_gurps_personagem),
):
    """Envia retrato (mesmo fluxo de arquivo que combatentes D&D 3.5)."""
    if not foto.filename:
        raise HTTPException(status_code=400, detail="Nenhum arquivo enviado")
    try:
        ent = service.obter_por_id(personagem_id)
        if ent.foto_url:
            file_service.deletar_arquivo(ent.foto_url)
        url = file_service.salvar_arquivo(foto)
        return service.atualizar(personagem_id, GurpsPersonagemUpdate(foto_url=url))
    except InvalidFileError as e:
        raise HTTPException(status_code=400, detail=e.message)
