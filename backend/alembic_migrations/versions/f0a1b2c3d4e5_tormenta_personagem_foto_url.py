"""Adiciona foto_url em tormenta_personagens (retrato na ficha).

Revision ID: f0a1b2c3d4e5
Revises: e1f2a3b4c5d6
Create Date: 2026-05-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f0a1b2c3d4e5"
down_revision: Union[str, None] = "e1f2a3b4c5d6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tormenta_personagens",
        sa.Column("foto_url", sa.String(length=2048), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tormenta_personagens", "foto_url")
