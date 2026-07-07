"""HTTP — campanhas Tormenta 20."""

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.dependencies import (
    get_tormenta_campanha_service,
    get_tormenta_campanha_solicitacao_service,
    get_tormenta_sessao_campanha_service,
)
from app.games.tormenta.schemas.campanha import (
    TormentaCampanhaAssociarPersonagens,
    TormentaCampanhaCreate,
    TormentaCampanhaResponse,
    TormentaCampanhaUpdate,
)
from app.games.tormenta.schemas.campanha_solicitacao import (
    TormentaCampanhaDisponivelResponse,
    TormentaCampanhaSolicitacaoCreate,
    TormentaCampanhaSolicitacaoResponse,
)
from app.games.tormenta.schemas.sessao_campanha import (
    TormentaSessaoCampanhaCreate,
    TormentaSessaoCampanhaResponse,
    TormentaSessaoCampanhaUpdate,
)
from app.games.tormenta.services.campanha_service import TormentaCampanhaService
from app.games.tormenta.services.campanha_solicitacao_service import (
    TormentaCampanhaSolicitacaoService,
)
from app.games.tormenta.services.sessao_campanha_service import (
    TormentaSessaoCampanhaService,
)
from app.shared.core.deps import get_usuario_atual, requer_game_tormenta
from app.shared.exceptions.custom_exceptions import ArenaBaseException, DadosInvalidos
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/tormenta/campanhas",
    tags=["Tormenta — Campanhas"],
    dependencies=[Depends(requer_game_tormenta)],
)


@router.get(
    "/sessoes/visiveis",
    response_model=list[TormentaSessaoCampanhaResponse],
)
def listar_sessoes_visiveis_para_jogador(
    service: TormentaSessaoCampanhaService = Depends(
        get_tormenta_sessao_campanha_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    rows = service.listar_visiveis_para_usuario(usuario.id)
    return [TormentaSessaoCampanhaResponse.model_validate(s) for s in rows]


@router.get("/sessoes", response_model=list[TormentaSessaoCampanhaResponse])
def listar_sessoes(
    service: TormentaSessaoCampanhaService = Depends(
        get_tormenta_sessao_campanha_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    rows = service.listar_para_mestre_ou_admin(usuario.perfil, usuario.id)
    return [TormentaSessaoCampanhaResponse.model_validate(s) for s in rows]


@router.post(
    "/sessoes",
    response_model=TormentaSessaoCampanhaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_sessao(
    payload: TormentaSessaoCampanhaCreate,
    service: TormentaSessaoCampanhaService = Depends(
        get_tormenta_sessao_campanha_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        s = service.criar(
            usuario_id=usuario.id,
            perfil=usuario.perfil,
            campanha_id=payload.campanha_id,
            resumo=payload.resumo,
            visivel_jogadores=payload.visivel_jogadores,
        )
        return TormentaSessaoCampanhaResponse.model_validate(s)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.put("/sessoes/{sessao_id}", response_model=TormentaSessaoCampanhaResponse)
def atualizar_sessao(
    sessao_id: int,
    payload: TormentaSessaoCampanhaUpdate,
    service: TormentaSessaoCampanhaService = Depends(
        get_tormenta_sessao_campanha_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        s = service.atualizar(
            usuario_id=usuario.id,
            perfil=usuario.perfil,
            sessao_id=sessao_id,
            resumo=payload.resumo,
            visivel_jogadores=payload.visivel_jogadores,
        )
        return TormentaSessaoCampanhaResponse.model_validate(s)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/sessoes/{sessao_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar_sessao(
    sessao_id: int,
    service: TormentaSessaoCampanhaService = Depends(
        get_tormenta_sessao_campanha_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        service.deletar(usuario.id, usuario.perfil, sessao_id)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return None


@router.get("/disponiveis", response_model=list[TormentaCampanhaDisponivelResponse])
def listar_disponiveis(
    service: TormentaCampanhaSolicitacaoService = Depends(
        get_tormenta_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    _ = usuario
    return service.listar_disponiveis()


@router.get(
    "/solicitacoes/pendentes",
    response_model=list[TormentaCampanhaSolicitacaoResponse],
)
def listar_solicitacoes_pendentes(
    service: TormentaCampanhaSolicitacaoService = Depends(
        get_tormenta_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return service.listar_pendentes_mestre(usuario)


@router.get(
    "/solicitacoes/minhas",
    response_model=TormentaCampanhaSolicitacaoResponse | None,
)
def obter_minha_solicitacao(
    personagem_id: int = Query(..., ge=1),
    service: TormentaCampanhaSolicitacaoService = Depends(
        get_tormenta_campanha_solicitacao_service
    ),
    usuario: Usuario = Depends(get_usuario_atual),
):
    return service.obter_pendente_personagem(usuario, personagem_id)


@router.post(
    "/solicitacoes",
    response_model=TormentaCampanhaSolicitacaoResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar_solicitacao(
    payload: TormentaCampanhaSolicitacaoCreate,
    service: TormentaCampanhaSolicitacaoService = Depends(
        get_tormenta_campanha_solicitacao_service
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
    response_model=TormentaCampanhaSolicitacaoResponse,
)
def aceitar_solicitacao(
    solicitacao_id: int,
    service: TormentaCampanhaSolicitacaoService = Depends(
        get_tormenta_campanha_solicitacao_service
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
    response_model=TormentaCampanhaSolicitacaoResponse,
)
def recusar_solicitacao(
    solicitacao_id: int,
    service: TormentaCampanhaSolicitacaoService = Depends(
        get_tormenta_campanha_solicitacao_service
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
    service: TormentaCampanhaSolicitacaoService = Depends(
        get_tormenta_campanha_solicitacao_service
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


@router.get("", response_model=list[TormentaCampanhaResponse])
def listar(
    service: TormentaCampanhaService = Depends(get_tormenta_campanha_service),
    usuario: Usuario = Depends(get_usuario_atual),
):
    rows = service.listar_para_mestre_ou_admin(usuario.perfil, usuario.id)
    return [TormentaCampanhaResponse.model_validate(c) for c in rows]


@router.post(
    "",
    response_model=TormentaCampanhaResponse,
    status_code=status.HTTP_201_CREATED,
)
def criar(
    payload: TormentaCampanhaCreate,
    service: TormentaCampanhaService = Depends(get_tormenta_campanha_service),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        c = service.criar(
            mestre_id=usuario.id,
            nome=payload.nome,
            descricao=payload.descricao or "",
            personagem_ids=payload.personagem_ids,
        )
        return TormentaCampanhaResponse.model_validate(c)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.put("/{campanha_id}", response_model=TormentaCampanhaResponse)
def atualizar(
    campanha_id: int,
    payload: TormentaCampanhaUpdate,
    service: TormentaCampanhaService = Depends(get_tormenta_campanha_service),
    usuario: Usuario = Depends(get_usuario_atual),
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
        return TormentaCampanhaResponse.model_validate(c)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.post("/{campanha_id}/personagens", response_model=TormentaCampanhaResponse)
def associar_personagens(
    campanha_id: int,
    payload: TormentaCampanhaAssociarPersonagens,
    service: TormentaCampanhaService = Depends(get_tormenta_campanha_service),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        c = service.associar_personagens(
            campanha_id, usuario.id, usuario.perfil, payload.personagem_ids
        )
        return TormentaCampanhaResponse.model_validate(c)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.delete("/{campanha_id}", status_code=status.HTTP_204_NO_CONTENT)
def deletar(
    campanha_id: int,
    service: TormentaCampanhaService = Depends(get_tormenta_campanha_service),
    usuario: Usuario = Depends(get_usuario_atual),
):
    try:
        service.deletar(campanha_id, usuario.id, usuario.perfil)
    except ArenaBaseException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)
    return None
