"""Tabela tormenta_combates — sessão de Arena por utilizador.

Revision ID: e7f8a9b0c1d2
Revises: c0d1e2f3a4b6
Create Date: 2026-05-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e7f8a9b0c1d2"
down_revision: Union[str, None] = "c0d1e2f3a4b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tormenta_combates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("personagens_ids", sa.JSON(), nullable=False),
        sa.Column("turno_atual", sa.Integer(), nullable=True, server_default=sa.text("0")),
        sa.Column("rodada_atual", sa.Integer(), nullable=True, server_default=sa.text("1")),
        sa.Column("ativo", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_tormenta_combates_usuario_id", "tormenta_combates", ["usuario_id"], unique=False
    )
    op.create_index(
        "ix_tormenta_combates_usuario_ativo",
        "tormenta_combates",
        ["usuario_id", "ativo"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_tormenta_combates_usuario_ativo", table_name="tormenta_combates")
    op.drop_index("ix_tormenta_combates_usuario_id", table_name="tormenta_combates")
    op.drop_table("tormenta_combates")
