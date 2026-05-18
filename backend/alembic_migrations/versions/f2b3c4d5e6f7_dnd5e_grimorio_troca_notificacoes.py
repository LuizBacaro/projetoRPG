"""Grimório 5e — histórico de troca e notificações.

Revision ID: f2b3c4d5e6f7
Revises: e1d5e6f7a8b9
Create Date: 2026-05-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f2b3c4d5e6f7"
down_revision: Union[str, None] = "e1d5e6f7a8b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dnd5e_grimorio_historico_troca",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("classe", sa.String(length=50), nullable=False),
        sa.Column("magia_removida_id", sa.Integer(), nullable=False),
        sa.Column("magia_adicionada_id", sa.Integer(), nullable=False),
        sa.Column("nivel_personagem", sa.Integer(), nullable=False),
        sa.Column("realizada_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["personagem_id"], ["dnd5e_personagens.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["magia_removida_id"], ["dnd5e_magias.id"], ondelete="RESTRICT"
        ),
        sa.ForeignKeyConstraint(
            ["magia_adicionada_id"], ["dnd5e_magias.id"], ondelete="RESTRICT"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dnd5e_grimorio_historico_personagem",
        "dnd5e_grimorio_historico_troca",
        ["personagem_id"],
    )

    op.create_table(
        "dnd5e_grimorio_notificacoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("classe", sa.String(length=50), nullable=False),
        sa.Column("tipo", sa.String(length=40), nullable=False),
        sa.Column("dados", sa.Text(), nullable=True),
        sa.Column("lida", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("criada_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["personagem_id"], ["dnd5e_personagens.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dnd5e_grimorio_notif_personagem_classe_lida",
        "dnd5e_grimorio_notificacoes",
        ["personagem_id", "classe", "lida"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_dnd5e_grimorio_notif_personagem_classe_lida",
        table_name="dnd5e_grimorio_notificacoes",
    )
    op.drop_table("dnd5e_grimorio_notificacoes")
    op.drop_index(
        "ix_dnd5e_grimorio_historico_personagem",
        table_name="dnd5e_grimorio_historico_troca",
    )
    op.drop_table("dnd5e_grimorio_historico_troca")
