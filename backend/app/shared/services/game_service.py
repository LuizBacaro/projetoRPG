"""
Service da camada multi-jogo.
SRP: orquestra catálogo de jogos, memberships e troca de jogo ativo.

Política multi-jogo:
- Jogos `disponiveis` no catálogo podem ser selecionados; `em_breve` continua
  bloqueado em `selecionar_jogo`.
- Membership é criado on-demand para slugs em `AUTO_ENROLL_MEMBERSHIP_GAME_SLUGS`
  (ex.: `dnd35`, `gurps`) quando o usuário entra no jogo ou carrega o catálogo.
"""

from datetime import timedelta
from typing import List, Optional, Tuple

from fastapi import HTTPException, status

from ...shared.core.config import settings
from ..constants import AUTO_ENROLL_MEMBERSHIP_GAME_SLUGS, GAME_SLUG_DND35
from ..core.security import criar_token
from ..models.game import Game, UserGameMembership
from ..models.usuario import Usuario
from ..ports import GameRepositoryProtocol, UserGameMembershipRepositoryProtocol
from ..schemas.game import (
    PERFIS_VALIDOS_NO_JOGO,
    GameResponse,
    MembershipAdminCreate,
    MembershipAdminItem,
    MembershipAdminListResponse,
    MembershipAdminUpdate,
    TokenComJogoResponse,
    UserGameMembershipResponse,
)


class GameService:
    def __init__(
        self,
        game_repository: GameRepositoryProtocol,
        membership_repository: UserGameMembershipRepositoryProtocol,
    ):
        self.games = game_repository
        self.memberships = membership_repository

    # ── Listagens ────────────────────────────────────────────────────────

    def listar_catalogo(self) -> List[GameResponse]:
        return [GameResponse.model_validate(g) for g in self.games.listar_disponiveis()]

    def listar_memberships(self, usuario: Usuario) -> List[UserGameMembershipResponse]:
        memberships = self.memberships.listar_por_usuario(usuario.id)
        return [
            UserGameMembershipResponse(
                id=m.id,
                game_id=m.game_id,
                game_slug=g.slug,
                game_nome=g.nome,
                game_status=g.status,
                perfil_no_jogo=m.perfil_no_jogo,
                ativo=m.ativo,
            )
            for (m, g) in memberships
        ]

    # ── Auto-enroll para registros novos ────────────────────────────────

    def _garantir_membership_para_slug(
        self, usuario: Usuario, slug: str
    ) -> Optional[Tuple[UserGameMembership, Game]]:
        existente = self.memberships.buscar_por_usuario_e_slug(usuario.id, slug)
        if existente is not None:
            return existente

        game = self.games.get_by_slug(slug)
        if game is None:
            return None

        perfil_valor = (
            usuario.perfil.value
            if hasattr(usuario.perfil, "value")
            else str(usuario.perfil)
        )
        novo = self.memberships.criar(
            UserGameMembership(
                usuario_id=usuario.id,
                game_id=game.id,
                perfil_no_jogo=perfil_valor,
                ativo=True,
            )
        )
        return novo, game

    def garantir_membership_padrao(
        self, usuario: Usuario
    ) -> Optional[Tuple[UserGameMembership, Game]]:
        """
        Garante membership no jogo padrão D&D 3.5 (compatível com chamadas legadas).
        """
        return self._garantir_membership_para_slug(usuario, GAME_SLUG_DND35)

    def garantir_auto_enroll_memberships(self, usuario: Usuario) -> None:
        """Cria memberships em jogos com auto-enroll (D&D 3.5, GURPS, …)."""
        for slug in AUTO_ENROLL_MEMBERSHIP_GAME_SLUGS:
            self._garantir_membership_para_slug(usuario, slug)

    # ── Seleção de jogo ─────────────────────────────────────────────────

    def selecionar_jogo(self, usuario: Usuario, game_slug: str) -> TokenComJogoResponse:
        slug = (game_slug or "").strip().lower()
        if not slug:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="game_slug é obrigatório",
            )

        game = self.games.get_by_slug(slug)
        if game is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Jogo '{slug}' não está no catálogo",
            )

        if game.status != "disponivel":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"O jogo '{game.nome}' ainda não está disponível "
                    f"(status: {game.status})."
                ),
            )

        par = self.memberships.buscar_por_usuario_e_slug(usuario.id, slug)
        if par is None:
            if slug in AUTO_ENROLL_MEMBERSHIP_GAME_SLUGS:
                par = self._garantir_membership_para_slug(usuario, slug)
            if par is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=(
                        f"Você ainda não tem acesso ao jogo '{game.nome}'. "
                        "Solicite ao administrador da plataforma."
                    ),
                )

        membership, game = par
        if not membership.ativo:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Seu acesso ao jogo '{game.nome}' está desativado.",
            )

        perfil = membership.perfil_no_jogo
        novo_access_token = criar_token(
            data={
                "sub": usuario.email,
                "game_slug": game.slug,
                "perfil_no_jogo": perfil,
                # Alias alinhado a docs de arquitetura multi-repo (`profile` = papel no jogo ativo).
                "profile": perfil,
            },
            secret_key=settings.SECRET_KEY,
            expires_delta=timedelta(hours=24),
            token_type="access",
        )
        novo_refresh_token = criar_token(
            data={
                "sub": usuario.email,
                "game_slug": game.slug,
                "perfil_no_jogo": perfil,
                "profile": perfil,
            },
            secret_key=settings.SECRET_KEY,
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
            token_type="refresh",
        )

        return TokenComJogoResponse(
            access_token=novo_access_token,
            refresh_token=novo_refresh_token,
            token_type="bearer",
            game_slug=game.slug,
            game_nome=game.nome,
            perfil_no_jogo=membership.perfil_no_jogo,
            usuario={
                "id": usuario.id,
                "email": usuario.email,
                "nome": usuario.nome,
                "perfil": (
                    usuario.perfil.value
                    if hasattr(usuario.perfil, "value")
                    else str(usuario.perfil)
                ),
                "ativo": usuario.ativo,
            },
        )

    # ── Admin: gestão de memberships ────────────────────────────────────

    def _validar_perfil_no_jogo(self, perfil: Optional[str]) -> Optional[str]:
        if perfil is None:
            return None
        normalizado = (perfil or "").strip().lower()
        if normalizado not in PERFIS_VALIDOS_NO_JOGO:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"perfil_no_jogo inválido: '{perfil}'. "
                    f"Valores permitidos: {sorted(PERFIS_VALIDOS_NO_JOGO)}."
                ),
            )
        return normalizado

    def _exigir_game_por_slug(self, slug: str) -> Game:
        game = self.games.get_by_slug(slug)
        if game is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Jogo '{slug}' não encontrado",
            )
        return game

    def _serializar_membership_admin(
        self, membership: UserGameMembership, usuario: Usuario
    ) -> MembershipAdminItem:
        return MembershipAdminItem(
            id=membership.id,
            usuario_id=usuario.id,
            usuario_nome=usuario.nome,
            usuario_email=usuario.email,
            usuario_perfil_global=(
                usuario.perfil.value
                if hasattr(usuario.perfil, "value")
                else str(usuario.perfil)
            ),
            perfil_no_jogo=membership.perfil_no_jogo,
            ativo=membership.ativo,
        )

    def listar_memberships_de_jogo_admin(
        self, game_slug: str
    ) -> MembershipAdminListResponse:
        game = self._exigir_game_por_slug(game_slug)
        rows = self.memberships.listar_memberships_de_jogo(game.id)
        return MembershipAdminListResponse(
            game_slug=game.slug,
            game_nome=game.nome,
            total=len(rows),
            items=[self._serializar_membership_admin(m, u) for m, u in rows],
        )

    def conceder_membership_admin(
        self, game_slug: str, payload: MembershipAdminCreate
    ) -> MembershipAdminItem:
        from ..models.usuario import Usuario as UsuarioModel  # late import

        game = self._exigir_game_por_slug(game_slug)

        usuario = (
            self.memberships.db.query(UsuarioModel)
            .filter(UsuarioModel.id == payload.usuario_id)
            .first()
        )
        if usuario is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Usuário id={payload.usuario_id} não encontrado",
            )

        existente = self.memberships.buscar_por_usuario_e_game_id(usuario.id, game.id)
        if existente is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Usuário '{usuario.email}' já possui acesso ao "
                    f"jogo '{game.nome}'."
                ),
            )

        perfil_no_jogo = self._validar_perfil_no_jogo(payload.perfil_no_jogo)
        if perfil_no_jogo is None:
            perfil_no_jogo = (
                usuario.perfil.value
                if hasattr(usuario.perfil, "value")
                else str(usuario.perfil)
            )

        novo = self.memberships.criar(
            UserGameMembership(
                usuario_id=usuario.id,
                game_id=game.id,
                perfil_no_jogo=perfil_no_jogo,
                ativo=bool(payload.ativo),
            )
        )
        return self._serializar_membership_admin(novo, usuario)

    def atualizar_membership_admin(
        self,
        game_slug: str,
        membership_id: int,
        payload: MembershipAdminUpdate,
    ) -> MembershipAdminItem:
        from ..models.usuario import Usuario as UsuarioModel

        game = self._exigir_game_por_slug(game_slug)
        membership = self.memberships.get_by_id(membership_id)
        if membership is None or membership.game_id != game.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Membership id={membership_id} não encontrado no "
                    f"jogo '{game.slug}'."
                ),
            )

        if payload.perfil_no_jogo is not None:
            membership.perfil_no_jogo = self._validar_perfil_no_jogo(
                payload.perfil_no_jogo
            )
        if payload.ativo is not None:
            membership.ativo = bool(payload.ativo)

        atualizado = self.memberships.atualizar(membership)
        usuario = (
            self.memberships.db.query(UsuarioModel)
            .filter(UsuarioModel.id == atualizado.usuario_id)
            .first()
        )
        return self._serializar_membership_admin(atualizado, usuario)

    def revogar_membership_admin(self, game_slug: str, membership_id: int) -> None:
        game = self._exigir_game_por_slug(game_slug)
        membership = self.memberships.get_by_id(membership_id)
        if membership is None or membership.game_id != game.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=(
                    f"Membership id={membership_id} não encontrado no "
                    f"jogo '{game.slug}'."
                ),
            )
        self.memberships.deletar(membership)
