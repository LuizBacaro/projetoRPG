"""Adicionar catálogo de jogos e tabela de membership por jogo.

Revision ID: a7b9d3e1c2f4
Revises: f6a1d2c3b4e5
Create Date: 2026-04-26

Introduz a camada multi-jogo da plataforma:
- `games_catalog`: catálogo global de sistemas de RPG suportados
- `user_game_memberships`: vínculo de cada usuário com cada jogo (perfil/ativo)

Mantém o D&D 3.5 como único jogo inicial via seed posterior em `init_db`.
Não toca em tabelas existentes — é aditiva e segura para rollout.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a7b9d3e1c2f4"
down_revision: Union[str, None] = "f6a1d2c3b4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existentes = set(inspector.get_table_names())

    if "games_catalog" not in existentes:
        op.create_table(
            "games_catalog",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("slug", sa.String(length=40), nullable=False),
            sa.Column("nome", sa.String(length=120), nullable=False),
            sa.Column("descricao", sa.String(length=500), nullable=True),
            sa.Column(
                "status",
                sa.String(length=20),
                nullable=False,
                server_default=sa.text("'disponivel'"),
            ),
            sa.Column("icone", sa.String(length=20), nullable=True),
            sa.Column(
                "ordem", sa.Integer(), nullable=False, server_default=sa.text("0")
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("slug", name="uq_games_catalog_slug"),
        )
        op.create_index(
            "ix_games_catalog_slug", "games_catalog", ["slug"], unique=True
        )

    if "user_game_memberships" not in existentes:
        op.create_table(
            "user_game_memberships",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("usuario_id", sa.Integer(), nullable=False),
            sa.Column("game_id", sa.Integer(), nullable=False),
            sa.Column("perfil_no_jogo", sa.String(length=20), nullable=False),
            sa.Column(
                "ativo", sa.Boolean(), nullable=False, server_default=sa.text("1")
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"]),
            sa.ForeignKeyConstraint(["game_id"], ["games_catalog.id"]),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint(
                "usuario_id", "game_id", name="uq_user_game_membership"
            ),
        )
        op.create_index(
            "ix_user_game_memberships_usuario_id",
            "user_game_memberships",
            ["usuario_id"],
            unique=False,
        )
        op.create_index(
            "ix_user_game_memberships_game_id",
            "user_game_memberships",
            ["game_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existentes = set(inspector.get_table_names())

    if "user_game_memberships" in existentes:
        op.drop_index(
            "ix_user_game_memberships_game_id", table_name="user_game_memberships"
        )
        op.drop_index(
            "ix_user_game_memberships_usuario_id",
            table_name="user_game_memberships",
        )
        op.drop_table("user_game_memberships")

    if "games_catalog" in existentes:
        op.drop_index("ix_games_catalog_slug", table_name="games_catalog")
        op.drop_table("games_catalog")
