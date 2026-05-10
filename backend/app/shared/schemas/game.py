"""
Schemas Pydantic para a camada multi-jogo (Auth Hub).
SRP: contratos de catálogo de jogos, memberships e troca de jogo ativo.
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GameResponse(BaseModel):
    """Entrada do catálogo global de jogos disponíveis."""

    id: int
    slug: str
    nome: str
    descricao: str = ""
    status: str = "disponivel"
    icone: str = ""
    ordem: int = 0

    model_config = ConfigDict(from_attributes=True)


class UserGameMembershipResponse(BaseModel):
    """Vínculo do usuário logado com um jogo específico."""

    id: int
    game_id: int
    game_slug: str
    game_nome: str
    game_status: str
    perfil_no_jogo: str
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


class SelecaoJogoRequest(BaseModel):
    """Payload para selecionar/trocar o jogo ativo da sessão."""

    game_slug: str = Field(..., min_length=1, max_length=40)


class TokenComJogoResponse(BaseModel):
    """
    Resposta de troca de jogo: novo access_token com claim `game_slug`,
    refresh_token preservado e dados consolidados do membership ativo.
    """

    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    game_slug: str
    game_nome: str
    perfil_no_jogo: str
    usuario: dict


class CatalogoJogosResponse(BaseModel):
    """Resposta agregada usada pelo seletor de jogo do frontend."""

    jogos: List[GameResponse]
    memberships: List[UserGameMembershipResponse]
    game_slug_ativo: Optional[str] = None
    auto_enter_last_game: bool = True
    server_time: datetime


# ── Admin: gestão de memberships ────────────────────────────────────────────

PERFIS_VALIDOS_NO_JOGO = {"jogador", "mestre", "administrador"}


class MembershipAdminItem(BaseModel):
    """Linha exibida no painel admin de memberships de um jogo."""

    id: int
    usuario_id: int
    usuario_nome: str
    usuario_email: str
    usuario_perfil_global: str
    perfil_no_jogo: str
    ativo: bool

    model_config = ConfigDict(from_attributes=True)


class MembershipAdminListResponse(BaseModel):
    """Listagem de memberships de um jogo para o painel admin."""

    game_slug: str
    game_nome: str
    total: int
    items: List[MembershipAdminItem]


class MembershipAdminCreate(BaseModel):
    """Payload para conceder acesso de um usuário a um jogo."""

    usuario_id: int = Field(..., gt=0)
    perfil_no_jogo: Optional[str] = Field(
        default=None,
        description=(
            "Quando ausente, espelha o perfil global do usuário. "
            "Permite que admins divirjam (ex.: usuário jogador globalmente "
            "vira mestre em D&D 5e)."
        ),
    )
    ativo: bool = True


class MembershipAdminUpdate(BaseModel):
    """Payload para alterar perfil_no_jogo / ativo de um membership."""

    perfil_no_jogo: Optional[str] = None
    ativo: Optional[bool] = None
