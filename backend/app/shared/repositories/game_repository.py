"""
Repository para o catálogo de jogos e memberships por usuário.
SRP: apenas acesso a dados da camada multi-jogo.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:
    from ..models.usuario import Usuario

from sqlalchemy.orm import Session

from ..models.game import Game, UserGameMembership


class GameRepository:
    """Acesso ao catálogo global de jogos suportados."""

    def __init__(self, db: Session):
        self.db = db

    def listar_disponiveis(self) -> List[Game]:
        return self.db.query(Game).order_by(Game.ordem.asc(), Game.nome.asc()).all()

    def get_by_slug(self, slug: str) -> Optional[Game]:
        if not slug:
            return None
        return self.db.query(Game).filter(Game.slug == slug.strip().lower()).first()

    def get_by_id(self, game_id: int) -> Optional[Game]:
        return self.db.query(Game).filter(Game.id == game_id).first()


class UserGameMembershipRepository:
    """Acesso aos vínculos usuário-jogo."""

    def __init__(self, db: Session):
        self.db = db

    def listar_por_usuario(
        self, usuario_id: int
    ) -> List[Tuple[UserGameMembership, Game]]:
        """Lista memberships do usuário com o Game associado em uma única query."""
        rows = (
            self.db.query(UserGameMembership, Game)
            .join(Game, Game.id == UserGameMembership.game_id)
            .filter(UserGameMembership.usuario_id == usuario_id)
            .order_by(Game.ordem.asc(), Game.nome.asc())
            .all()
        )
        return [(membership, game) for membership, game in rows]

    def buscar_por_usuario_e_slug(
        self, usuario_id: int, slug: str
    ) -> Optional[Tuple[UserGameMembership, Game]]:
        if not slug:
            return None
        row = (
            self.db.query(UserGameMembership, Game)
            .join(Game, Game.id == UserGameMembership.game_id)
            .filter(
                UserGameMembership.usuario_id == usuario_id,
                Game.slug == slug.strip().lower(),
            )
            .first()
        )
        if row is None:
            return None
        membership, game = row
        return membership, game

    def criar(self, membership: UserGameMembership) -> UserGameMembership:
        self.db.add(membership)
        self.db.commit()
        self.db.refresh(membership)
        return membership

    # ── Operações administrativas ───────────────────────────────────────

    def listar_memberships_de_jogo(
        self, game_id: int
    ) -> List[Tuple[UserGameMembership, Usuario]]:
        """
        Lista todos os memberships de um jogo com o Usuário em uma única query.
        Usado no painel admin para gerenciar acesso a um jogo específico.
        """
        from ..models.usuario import Usuario

        rows = (
            self.db.query(UserGameMembership, Usuario)
            .join(Usuario, Usuario.id == UserGameMembership.usuario_id)
            .filter(UserGameMembership.game_id == game_id)
            .order_by(Usuario.nome.asc())
            .all()
        )
        return [(m, u) for m, u in rows]

    def get_by_id(self, membership_id: int) -> Optional[UserGameMembership]:
        return (
            self.db.query(UserGameMembership)
            .filter(UserGameMembership.id == membership_id)
            .first()
        )

    def buscar_por_usuario_e_game_id(
        self, usuario_id: int, game_id: int
    ) -> Optional[UserGameMembership]:
        return (
            self.db.query(UserGameMembership)
            .filter(
                UserGameMembership.usuario_id == usuario_id,
                UserGameMembership.game_id == game_id,
            )
            .first()
        )

    def atualizar(self, membership: UserGameMembership) -> UserGameMembership:
        self.db.commit()
        self.db.refresh(membership)
        return membership

    def deletar(self, membership: UserGameMembership) -> None:
        self.db.delete(membership)
        self.db.commit()
