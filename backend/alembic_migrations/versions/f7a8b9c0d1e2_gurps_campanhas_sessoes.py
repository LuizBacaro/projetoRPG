"""GURPS: sessões de campanha (resumo + visível aos jogadores).

Revision ID: f7a8b9c0d1e2
Revises: e8f9a0b1c2d3
Create Date: 2026-05-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f7a8b9c0d1e2"
down_revision: Union[str, None] = "e8f9a0b1c2d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gurps_campanhas_sessoes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("campanha_id", sa.Integer(), nullable=False),
        sa.Column("resumo", sa.String(length=4000), nullable=False),
        sa.Column(
            "visivel_jogadores",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
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
        sa.ForeignKeyConstraint(
            ["campanha_id"],
            ["gurps_campanhas.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_gurps_campanhas_sessoes_id",
        "gurps_campanhas_sessoes",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_gurps_campanhas_sessoes_campanha_id",
        "gurps_campanhas_sessoes",
        ["campanha_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_gurps_campanhas_sessoes_campanha_id",
        table_name="gurps_campanhas_sessoes",
    )
    op.drop_index("ix_gurps_campanhas_sessoes_id", table_name="gurps_campanhas_sessoes")
    op.drop_table("gurps_campanhas_sessoes")
