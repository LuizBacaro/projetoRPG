"""add_combate_historico_table

Revision ID: f2a7b1c4d9e0
Revises: e4a1f9c8d2b3
Create Date: 2026-03-29 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2a7b1c4d9e0"
down_revision: Union[str, None] = "e4a1f9c8d2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "combates_historico",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("combate_id", sa.Integer(), nullable=True),
        sa.Column("combatentes_ids", sa.JSON(), nullable=False),
        sa.Column("total_combatentes", sa.Integer(), nullable=False),
        sa.Column("total_vivos", sa.Integer(), nullable=False),
        sa.Column("total_rodadas", sa.Integer(), nullable=False),
        sa.Column("total_turnos", sa.Integer(), nullable=False),
        sa.Column("vencedor_id", sa.Integer(), nullable=True),
        sa.Column("vencedor_nome", sa.String(length=120), nullable=True),
        sa.Column("vencedor_tipo", sa.String(length=20), nullable=True),
        sa.Column("motivo_encerramento", sa.String(length=40), nullable=False),
        sa.Column("estatisticas", sa.JSON(), nullable=False),
        sa.Column("finalizado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_combates_historico_id", "combates_historico", ["id"], unique=False)
    op.create_index("ix_combates_historico_combate_id", "combates_historico", ["combate_id"], unique=False)
    op.create_index("ix_combates_historico_finalizado_em", "combates_historico", ["finalizado_em"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_combates_historico_finalizado_em", table_name="combates_historico")
    op.drop_index("ix_combates_historico_combate_id", table_name="combates_historico")
    op.drop_index("ix_combates_historico_id", table_name="combates_historico")
    op.drop_table("combates_historico")
