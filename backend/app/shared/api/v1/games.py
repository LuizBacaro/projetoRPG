"""
Rotas da camada multi-jogo (Auth Hub).
SRP: catálogo global, memberships do usuário e seleção de jogo ativo.

Estas rotas formam a fronteira que, em fases futuras, poderá ser extraída
para um serviço Auth Hub independente (ver docs/arquitetura-multi-jogo.md).
Hoje convivem com o backend D&D 3.5 mas não acoplam regras de jogo.
"""
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, status

from ...core.deps import get_usuario_atual, extrair_token_do_header, requer_admin
from ...core.security import decodificar_token
from ...core.config import settings
from app.core.dependencies import get_game_service
from ...models.usuario import Usuario
from ...schemas.game import (
    CatalogoJogosResponse,
    SelecaoJogoRequest,
    TokenComJogoResponse,
    MembershipAdminListResponse,
    MembershipAdminItem,
    MembershipAdminCreate,
    MembershipAdminUpdate,
)
from ...services.game_service import GameService
from starlette.requests import Request


router = APIRouter(
    prefix="/games",
    tags=["games"],
)


@router.get(
    "",
    response_model=CatalogoJogosResponse,
    status_code=status.HTTP_200_OK,
    summary="Catálogo + memberships do usuário",
    description=(
        "Retorna o catálogo global de jogos suportados pela plataforma e os "
        "vínculos do usuário autenticado. Indica qual jogo está ativo na "
        "sessão atual via claim `game_slug` do token."
    ),
)
def listar_catalogo(
    request: Request,
    usuario: Usuario = Depends(get_usuario_atual),
    service: GameService = Depends(get_game_service),
) -> CatalogoJogosResponse:
    catalogo = service.listar_catalogo()

    service.garantir_membership_padrao(usuario)

    memberships = service.listar_memberships(usuario)

    game_slug_ativo = None
    token = extrair_token_do_header(request)
    if token:
        payload = decodificar_token(token, settings.SECRET_KEY)
        if payload:
            game_slug_ativo = payload.get("game_slug")

    return CatalogoJogosResponse(
        jogos=catalogo,
        memberships=memberships,
        game_slug_ativo=game_slug_ativo,
        auto_enter_last_game=settings.AUTO_ENTER_LAST_GAME,
        server_time=datetime.now(timezone.utc),
    )


@router.post(
    "/selecionar",
    response_model=TokenComJogoResponse,
    status_code=status.HTTP_200_OK,
    summary="Selecionar jogo ativo",
    description=(
        "Emite novos tokens (access + refresh) carregando o claim `game_slug` "
        "para o jogo escolhido. Esses tokens passam a ser usados em todas as "
        "chamadas subsequentes do frontend daquele jogo."
    ),
    responses={
        404: {"description": "Jogo não cadastrado"},
        409: {"description": "Jogo ainda não está disponível"},
        403: {"description": "Sem acesso ao jogo selecionado"},
    },
)
def selecionar_jogo(
    payload: SelecaoJogoRequest,
    usuario: Usuario = Depends(get_usuario_atual),
    service: GameService = Depends(get_game_service),
) -> TokenComJogoResponse:
    return service.selecionar_jogo(usuario, payload.game_slug)


# ── Admin: gestão de memberships por jogo ──────────────────────────────────


@router.get(
    "/{game_slug}/memberships",
    response_model=MembershipAdminListResponse,
    status_code=status.HTTP_200_OK,
    summary="[admin] Listar acessos de um jogo",
    description=(
        "Retorna todos os usuários com acesso ao jogo `game_slug`, com perfil "
        "específico no jogo e flag `ativo`. Restrito a administradores globais."
    ),
)
def admin_listar_memberships(
    game_slug: str,
    _admin: Usuario = Depends(requer_admin),
    service: GameService = Depends(get_game_service),
) -> MembershipAdminListResponse:
    return service.listar_memberships_de_jogo_admin(game_slug)


@router.post(
    "/{game_slug}/memberships",
    response_model=MembershipAdminItem,
    status_code=status.HTTP_201_CREATED,
    summary="[admin] Conceder acesso de usuário a um jogo",
    description=(
        "Cria um membership para `usuario_id` no jogo `game_slug`. "
        "`perfil_no_jogo` é opcional — quando omitido, espelha o perfil global "
        "do usuário; quando informado, permite divergir (ex.: jogador global "
        "vira mestre em D&D 5e)."
    ),
    responses={
        404: {"description": "Jogo ou usuário não encontrado"},
        409: {"description": "Usuário já tem acesso a esse jogo"},
        422: {"description": "perfil_no_jogo inválido"},
    },
)
def admin_conceder_membership(
    game_slug: str,
    payload: MembershipAdminCreate,
    _admin: Usuario = Depends(requer_admin),
    service: GameService = Depends(get_game_service),
) -> MembershipAdminItem:
    return service.conceder_membership_admin(game_slug, payload)


@router.patch(
    "/{game_slug}/memberships/{membership_id}",
    response_model=MembershipAdminItem,
    status_code=status.HTTP_200_OK,
    summary="[admin] Atualizar perfil/ativo de um membership",
    responses={
        404: {"description": "Membership não encontrado"},
        422: {"description": "perfil_no_jogo inválido"},
    },
)
def admin_atualizar_membership(
    game_slug: str,
    membership_id: int,
    payload: MembershipAdminUpdate,
    _admin: Usuario = Depends(requer_admin),
    service: GameService = Depends(get_game_service),
) -> MembershipAdminItem:
    return service.atualizar_membership_admin(game_slug, membership_id, payload)


@router.delete(
    "/{game_slug}/memberships/{membership_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="[admin] Revogar acesso de usuário a um jogo",
    responses={404: {"description": "Membership não encontrado"}},
)
def admin_revogar_membership(
    game_slug: str,
    membership_id: int,
    _admin: Usuario = Depends(requer_admin),
    service: GameService = Depends(get_game_service),
) -> None:
    service.revogar_membership_admin(game_slug, membership_id)
    return None
