"""Tabela tormenta_magias_personagem — grimório / conhecidas / preparadas (slug catálogo MB).

Revision ID: a3c5e7d9b1f0
Revises: e7f8a9b0c1d2
Create Date: 2026-05-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3c5e7d9b1f0"
down_revision: Union[str, None] = "e7f8a9b0c1d2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tormenta_magias_personagem",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("magia_slug", sa.String(length=80), nullable=False),
        sa.Column("papel", sa.String(length=20), nullable=False),
        sa.Column("notas", sa.String(length=500), nullable=True),
        sa.Column("adicionado_em", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "papel IN ('grimorio', 'conhecida', 'preparada')",
            name="ck_tormenta_magia_personagem_papel",
        ),
        sa.ForeignKeyConstraint(
            ["personagem_id"],
            ["tormenta_personagens.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "personagem_id",
            "magia_slug",
            "papel",
            name="uq_tormenta_magia_personagem_par",
        ),
    )
    op.create_index(
        "ix_tormenta_magias_personagem_id",
        "tormenta_magias_personagem",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_tormenta_magias_personagem_personagem_id",
        "tormenta_magias_personagem",
        ["personagem_id"],
        unique=False,
    )
    op.create_index(
        "ix_tormenta_magias_personagem_magia_slug",
        "tormenta_magias_personagem",
        ["magia_slug"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_tormenta_magias_personagem_magia_slug",
        table_name="tormenta_magias_personagem",
    )
    op.drop_index(
        "ix_tormenta_magias_personagem_personagem_id",
        table_name="tormenta_magias_personagem",
    )
    op.drop_index(
        "ix_tormenta_magias_personagem_id",
        table_name="tormenta_magias_personagem",
    )
    op.drop_table("tormenta_magias_personagem")
