"""tormenta_combates.condicoes_mb_json — condições MB da arena por personagem.

Revision ID: b4d6e8f0a2c1
Revises: a3c5e7d9b1f0
Create Date: 2026-05-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b4d6e8f0a2c1"
down_revision: Union[str, None] = "a3c5e7d9b1f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "tormenta_combates",
        sa.Column("condicoes_mb_json", sa.JSON(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("tormenta_combates", "condicoes_mb_json")
