"""Adicionar tabela de sessões de campanha.

Revision ID: f6a1d2c3b4e5
Revises: c1d2e3f4a5b6
Create Date: 2026-04-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f6a1d2c3b4e5"
down_revision: Union[str, None] = "c1d2e3f4a5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "campanhas_sessoes" in inspector.get_table_names():
        return

    op.create_table(
        "campanhas_sessoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campanha_id", sa.Integer(), nullable=False),
        sa.Column("resumo", sa.String(length=4000), nullable=False),
        sa.Column("visivel_jogadores", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["campanha_id"], ["campanhas.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_campanhas_sessoes_id", "campanhas_sessoes", ["id"], unique=False)
    op.create_index("ix_campanhas_sessoes_campanha_id", "campanhas_sessoes", ["campanha_id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "campanhas_sessoes" not in inspector.get_table_names():
        return
    op.drop_index("ix_campanhas_sessoes_campanha_id", table_name="campanhas_sessoes")
    op.drop_index("ix_campanhas_sessoes_id", table_name="campanhas_sessoes")
    op.drop_table("campanhas_sessoes")
