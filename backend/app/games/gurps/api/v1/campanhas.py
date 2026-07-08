"""HTTP — campanhas GURPS."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import (
    get_gurps_campanha_service,
    get_gurps_campanha_solicitacao_service,
    get_gurps_sessao_campanha_service,
)
from app.games.gurps.schemas.campanha import (
    GurpsCampanhaAssociarPersonagens,
    GurpsCampanhaCreate,
    GurpsCampanhaResponse,
    GurpsCampanhaUpdate,
)
from app.games.gurps.schemas.campanha_solicitacao import (
    GurpsCampanhaDisponivelResponse,
    GurpsCampanhaSolicitacaoCreate,
    GurpsCampanhaSolicitacaoResponse,
)
from app.games.gurps.schemas.sessao_campanha import (
    GurpsSessaoCampanhaCreate,
    GurpsSessaoCampanhaResponse,
    GurpsSessaoCampanhaUpdate,
)
from app.games.gurps.services.campanha_service import GurpsCampanhaService
from app.games.gurps.services.campanha_solicitacao_service import (
    GurpsCampanhaSolicitacaoService,
)
from app.games.gurps.services.sessao_campanha_service import GurpsSessaoCampanhaService
from app.shared.core.deps import get_usuario_atual, requer_game_gurps
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/gurps/campanhas",
    tags=["GURPS — Campanhas"],
    dependencies=[Depends(requer_game_gurps)],
)


@router.get(
    "/sessoes/visiveis",
    response_model=list[GurpsSessaoCampanhaResponse],
)
def listar_sessoes_visiveis_para_jogador(
    service: GurpsSessaoCampanhaService = Depends(get_gurps_sessao_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    rows = service.listar_visiveis_para_usuario(usuario.id)
    return [GurpsSessaoCampanhaResponse.model_validate(s) for s in rows]


@router.get("/sessoes", response_model=list[GurpsSessaoCampanhaResponse])
def listar_sessoes(
    service: GurpsSessaoCampanhaService = Depends(get_gurps_sessao_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    rows = service.listar_para_mestre_ou_admin(usuario.perfil, usuario.id)
    return [GurpsSessaoCampanhaResponse.model_validate(s) for s in rows]


@router.post(
    "/sessoes",
    response_model=GurpsSessaoCampanhaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_sessao(
    payload: GurpsSessaoCampanhaCreate,
    service: GurpsSessaoCampanhaService = Depends(get_gurps_sessao_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        s = service.criar(
            usuario_id=usuario.id,
            perfil=usuario.perfil,
            campanha_id=payload.campanha_id,
            resumo=payload.resumo,
            visivel_jogadores=payload.visivel_jogadores,
        )
        return GurpsSessaoCampanhaResponse.model_validate(s)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.put("/sessoes/{sessao_id}", response_model=GurpsSessaoCampanhaResponse)
def atualizar_sessao(
    sessao_id: int,
    payload: GurpsSessaoCampanhaUpdate,
    service: GurpsSessaoCampanhaService = Depends(get_gurps_sessao_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        s = service.atualizar(
            usuario_id=usuario.id,
            perfil=usuario.perfil,
            sessao_id=sessao_id,
            resumo=payload.resumo,
            visivel_jogadores=payload.visivel_jogadores,
        )
        return GurpsSessaoCampanhaResponse.model_validate(s)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/sessoes/{sessao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_sessao(
    sessao_id: int,
    service: GurpsSessaoCampanhaService = Depends(get_gurps_sessao_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        service.deletar(usuario.id, usuario.perfil, sessao_id)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return None


@router.get("/disponiveis", response_model=list[GurpsCampanhaDisponivelResponse])
def listar_disponiveis(
    service: GurpsCampanhaSolicitacaoService = Depends(
        get_gurps_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    _ = usuario
    return service.listar_disponiveis()


@router.get(
    "/solicitacoes/pendentes",
    response_model=list[GurpsCampanhaSolicitacaoResponse],
)
def listar_solicitacoes_pendentes(
    service: GurpsCampanhaSolicitacaoService = Depends(
        get_gurps_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return service.listar_pendentes_mestre(usuario)


@router.get(
    "/solicitacoes/historico",
    response_model=list[GurpsCampanhaSolicitacaoResponse],
)
def listar_solicitacoes_historico(
    service: GurpsCampanhaSolicitacaoService = Depends(
        get_gurps_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return service.listar_historico_mestre(usuario)


@router.get(
    "/solicitacoes/minhas",
    response_model=GurpsCampanhaSolicitacaoResponse | None,
)
def obter_minha_solicitacao(
    personagem_id: int = Query(..., ge=1),
    service: GurpsCampanhaSolicitacaoService = Depends(
        get_gurps_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return service.obter_pendente_personagem(usuario, personagem_id)


@router.post(
    "/solicitacoes",
    response_model=GurpsCampanhaSolicitacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_solicitacao(
    payload: GurpsCampanhaSolicitacaoCreate,
    service: GurpsCampanhaSolicitacaoService = Depends(
        get_gurps_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        return service.criar_solicitacao(
            usuario, payload.campanha_id, payload.personagem_id
        )
    except DadosInvalidos as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post(
    "/solicitacoes/{solicitacao_id}/aceitar",
    response_model=GurpsCampanhaSolicitacaoResponse,
)
def aceitar_solicitacao(
    solicitacao_id: int,
    service: GurpsCampanhaSolicitacaoService = Depends(
        get_gurps_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        return service.aceitar(usuario, solicitacao_id)
    except DadosInvalidos as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.post(
    "/solicitacoes/{solicitacao_id}/recusar",
    response_model=GurpsCampanhaSolicitacaoResponse,
)
def recusar_solicitacao(
    solicitacao_id: int,
    service: GurpsCampanhaSolicitacaoService = Depends(
        get_gurps_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        return service.recusar(usuario, solicitacao_id)
    except DadosInvalidos as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc


@router.delete("/solicitacoes/{solicitacao_id}", status_code=status.HTTP_204_NO_CONTENT)
def cancelar_solicitacao(
    solicitacao_id: int,
    service: GurpsCampanhaSolicitacaoService = Depends(
        get_gurps_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        service.cancelar(usuario, solicitacao_id)
    except DadosInvalidos as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message) from exc
    return None


@router.get("", response_model=list[GurpsCampanhaResponse])
def listar(
    service: GurpsCampanhaService = Depends(get_gurps_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    rows = service.listar_para_mestre_ou_admin(usuario.perfil, usuario.id)
    return [GurpsCampanhaResponse.model_validate(c) for c in rows]


@router.post(
    "", response_model=GurpsCampanhaResponse, status_code=status.HTTP_201_CREATED
)
def criar(
    payload: GurpsCampanhaCreate,
    service: GurpsCampanhaService = Depends(get_gurps_campanha_service),
    usuario=Depends(get_usuario_atual),
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
    usuario=Depends(get_usuario_atual),
):
    try:
        c = service.atualizar(
            campanha_id=campanha_id,
            usuario_id=usuario.id,
            perfil=usuario.perfil,
            nome=payload.nome,
            descricao=payload.descricao,
            personagem_ids=payload.personagem_ids,
        )
        return GurpsCampanhaResponse.model_validate(c)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post("/{campanha_id}/personagens", response_model=GurpsCampanhaResponse)
def associar_personagens(
    campanha_id: int,
    payload: GurpsCampanhaAssociarPersonagens,
    service: GurpsCampanhaService = Depends(get_gurps_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        c = service.associar_personagens(
            campanha_id, usuario.id, usuario.perfil, payload.personagem_ids
        )
        return GurpsCampanhaResponse.model_validate(c)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{campanha_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(
    campanha_id: int,
    service: GurpsCampanhaService = Depends(get_gurps_campanha_service),
    usuario=Depends(get_usuario_atual),
):
    try:
        service.deletar(campanha_id, usuario.id, usuario.perfil)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
