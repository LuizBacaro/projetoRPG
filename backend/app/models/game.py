"""
Model de Game (catálogo) e UserGameMembership.
SRP: representa o catálogo global de jogos suportados pela plataforma multi-jogo
e o vínculo do usuário com cada jogo (perfil específico por jogo).

A camada multi-jogo permite que a mesma conta global selecione qual sistema
de RPG (D&D 3.5, D&D 5e, GURPS, etc.) deseja acessar após o login. Cada jogo
tem seu próprio domínio de dados (campanhas, fichas, regras), mas autenticação,
identidade e perfil global são únicos.
"""
from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Game(Base):
    """
    Catálogo global de jogos disponíveis na plataforma.

    `slug` é o identificador estável usado em tokens (`game_slug`), URLs e
    isolamento por jogo. `status` indica disponibilidade pública:
      - `disponivel`: usuário pode entrar no jogo
      - `em_breve`: aparece no seletor mas com bloqueio de acesso
      - `manutencao`: temporariamente indisponível
    """

    __tablename__ = "games_catalog"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(40), unique=True, nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    descricao = Column(String(500), nullable=True, default="")
    status = Column(String(20), nullable=False, default="disponivel")
    icone = Column(String(20), nullable=True, default="")
    ordem = Column(Integer, nullable=False, default=0)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    memberships = relationship(
        "UserGameMembership",
        back_populates="game",
        lazy="selectin",
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Game id={self.id} slug={self.slug} status={self.status}>"


class UserGameMembership(Base):
    """
    Vínculo de um usuário com um jogo específico.

    Permite ter perfis diferentes em jogos diferentes (ex.: jogador no D&D 3.5
    e mestre no D&D 5e). Por enquanto o `perfil_no_jogo` espelha o perfil global
    em `usuarios.perfil`, mas o modelo já suporta divergir no futuro sem migração.
    """

    __tablename__ = "user_game_memberships"
    __table_args__ = (
        UniqueConstraint("usuario_id", "game_id", name="uq_user_game_membership"),
    )

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=False, index=True
    )
    game_id = Column(
        Integer, ForeignKey("games_catalog.id"), nullable=False, index=True
    )
    perfil_no_jogo = Column(String(20), nullable=False)
    ativo = Column(Boolean, nullable=False, default=True)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    game = relationship("Game", back_populates="memberships", lazy="joined")

    def __repr__(self):
        return (
            f"<UserGameMembership usuario_id={self.usuario_id} "
            f"game_id={self.game_id} perfil={self.perfil_no_jogo}>"
        )
