"""HTTP — personagens D&D 5e."""

from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile

from app.core.dependencies import (
    get_dnd5e_conjuracao_ficha_service,
    get_dnd5e_personagem_service,
    get_dnd5e_progressao_service,
    get_file_service,
)
from app.games.dnd5e.schemas.personagem import (
    Dnd5ePersonagemCreate,
    Dnd5ePersonagemResponse,
    Dnd5ePersonagemUpdate,
)
from app.games.dnd5e.schemas.progressao import (
    Dnd5eExpertisePericiasRequest,
    Dnd5eExpertisePericiasResponse,
    Dnd5eFeatEscolhasRequest,
    Dnd5eFeatEscolhasResponse,
    Dnd5eHpRollRequest,
    Dnd5eHpRollResponse,
    Dnd5eMarcoRequest,
    Dnd5eMarcoResponse,
    Dnd5ePendenciasProgressaoResponse,
    Dnd5ePericiasOverrideRequest,
    Dnd5ePericiasOverrideResponse,
    Dnd5eRepousoLongoResponse,
)
from app.games.dnd5e.services.conjuracao_ficha_service import (
    Dnd5eConjuracaoFichaService,
)
from app.games.dnd5e.services.personagem_service import Dnd5ePersonagemService
from app.games.dnd5e.services.progressao_service import Dnd5eProgressaoService
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


@router.delete("/{personagem_id}", status_code=204)
def excluir(
    personagem_id: int,
    service: Dnd5ePersonagemService = Depends(get_dnd5e_personagem_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        service.excluir(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.get(
    "/{personagem_id}/progressao/pendencias",
    response_model=Dnd5ePendenciasProgressaoResponse,
    summary="Pendências de progressão (HP por nível, marcos feat/ASI)",
)
def progressao_pendencias(
    personagem_id: int,
    service: Dnd5eProgressaoService = Depends(get_dnd5e_progressao_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        return service.pendencias(personagem_id)
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post(
    "/{personagem_id}/progressao/hp-roll",
    response_model=Dnd5eHpRollResponse,
    summary="Registra rolagem de PV para um nível (2–20)",
)
def progressao_hp_roll(
    personagem_id: int,
    payload: Dnd5eHpRollRequest,
    service: Dnd5eProgressaoService = Depends(get_dnd5e_progressao_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        return service.registrar_hp_roll(
            personagem_id,
            nivel=payload.nivel,
            roll=payload.roll,
            usar_media=payload.usar_media,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/{personagem_id}/progressao/marco",
    response_model=Dnd5eMarcoResponse,
    summary="Registra marco de feat ou ASI (níveis 4/8/12/16/19)",
)
def progressao_marco(
    personagem_id: int,
    payload: Dnd5eMarcoRequest,
    service: Dnd5eProgressaoService = Depends(get_dnd5e_progressao_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        return service.registrar_marco(
            personagem_id,
            nivel=payload.nivel,
            tipo=payload.tipo,
            slug=payload.slug,
            distribuicao=payload.distribuicao,
            feat_escolhas=payload.feat_escolhas,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/{personagem_id}/progressao/feat-escolhas",
    response_model=Dnd5eFeatEscolhasResponse,
    summary="Atualiza escolhas de talentos (Resiliente, Iniciado em Magia)",
)
def progressao_feat_escolhas(
    personagem_id: int,
    payload: Dnd5eFeatEscolhasRequest,
    service: Dnd5eProgressaoService = Depends(get_dnd5e_progressao_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        return service.salvar_feat_escolhas(
            personagem_id,
            payload.feat_escolhas,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/{personagem_id}/progressao/pericias-override",
    response_model=Dnd5ePericiasOverrideResponse,
    summary="Atualiza proficiências manuais de perícias (multiclasse, feats, mesa)",
)
def progressao_pericias_override(
    personagem_id: int,
    payload: Dnd5ePericiasOverrideRequest,
    service: Dnd5eProgressaoService = Depends(get_dnd5e_progressao_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        return service.salvar_pericias_override(
            personagem_id,
            payload.pericias_override,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/{personagem_id}/progressao/expertise-pericias",
    response_model=Dnd5eExpertisePericiasResponse,
    summary="Escolhas de Expertise (Ladino/Bardo) — dobra bônus de proficiência",
)
def progressao_expertise_pericias(
    personagem_id: int,
    payload: Dnd5eExpertisePericiasRequest,
    service: Dnd5eProgressaoService = Depends(get_dnd5e_progressao_service),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        return service.salvar_expertise_pericias(
            personagem_id,
            payload.expertise_pericias,
        )
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
    except DadosInvalidos as e:
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post(
    "/{personagem_id}/repouso-longo",
    response_model=Dnd5eRepousoLongoResponse,
    summary="Repouso longo — recupera PV (1d8+CON/nível) e slots de magia",
)
def repouso_longo(
    personagem_id: int,
    prog_service: Dnd5eProgressaoService = Depends(get_dnd5e_progressao_service),
    conj_service: Dnd5eConjuracaoFichaService = Depends(
        get_dnd5e_conjuracao_ficha_service
    ),
    _: Usuario = Depends(requer_dono_ou_admin_dnd5e_personagem),
):
    try:
        res = prog_service.aplicar_repouso_longo(personagem_id)
        try:
            estado = conj_service.descanso_longo(personagem_id)
            res.conjuracao = estado.model_dump()
            if estado.slots:
                res.mensagem = (
                    f"{res.mensagem}; espaços de magia restaurados"
                    if res.mensagem
                    else "Espaços de magia restaurados"
                )
        except HTTPException:
            pass
        return res
    except ArenaBaseException as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


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
        return service.atualizar(personagem_id, Dnd5ePersonagemUpdate(foto_url=url))
    except InvalidFileError as e:
        raise HTTPException(status_code=400, detail=e.message)
