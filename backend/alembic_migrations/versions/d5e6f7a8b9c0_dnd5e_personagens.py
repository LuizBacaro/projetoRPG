"""Tabela dnd5e_personagens (ficha D&D 5e).

Revision ID: d5e6f7a8b9c0
Revises: f1a2b3c4d5e6
Create Date: 2026-05-16
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "d5e6f7a8b9c0"
down_revision: Union[str, None] = "f1a2b3c4d5e6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dnd5e_personagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dono_id", sa.Integer(), nullable=True),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("jogador_nome", sa.String(length=120), nullable=True),
        sa.Column("foto_url", sa.String(length=2048), nullable=True),
        sa.Column("nivel", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("experiencia", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("strength", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("dexterity", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("constitution", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("intelligence", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("wisdom", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("charisma", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("hp_max", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hp_atual", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ficha_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.CheckConstraint(
            "tipo IN ('jogador', 'monstro', 'npc')",
            name="ck_dnd5e_personagens_tipo_valido",
        ),
        sa.CheckConstraint(
            "nivel >= 1 AND nivel <= 20",
            name="ck_dnd5e_personagens_nivel",
        ),
        sa.ForeignKeyConstraint(["dono_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_dnd5e_personagens_id", "dnd5e_personagens", ["id"], unique=False
    )
    op.create_index(
        "ix_dnd5e_personagens_dono_id",
        "dnd5e_personagens",
        ["dono_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_dnd5e_personagens_dono_id", table_name="dnd5e_personagens")
    op.drop_index("ix_dnd5e_personagens_id", table_name="dnd5e_personagens")
    op.drop_table("dnd5e_personagens")
