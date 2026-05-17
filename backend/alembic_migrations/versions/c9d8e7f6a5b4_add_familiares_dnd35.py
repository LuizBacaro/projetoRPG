"""add_familiares_dnd35

Revision ID: c9d8e7f6a5b4
Revises: e8f1a2b3c4d5
Create Date: 2026-05-17 15:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9d8e7f6a5b4"
down_revision: Union[str, None] = "e8f1a2b3c4d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "familiares"):
        return

    op.create_table(
        "familiares",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("combatente_id", sa.Integer(), nullable=False),
        sa.Column("especie_slug", sa.String(length=60), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("nivel_mestre", sa.Integer(), nullable=False),
        sa.Column("inteligencia", sa.Integer(), nullable=False),
        sa.Column("armadura_natural_bonus", sa.Integer(), nullable=False),
        sa.Column("hp_atual", sa.Integer(), nullable=False),
        sa.Column("hp_maximo", sa.Integer(), nullable=False),
        sa.Column("ca", sa.Integer(), nullable=False),
        sa.Column("bonus_mestre", sa.String(length=200), nullable=False),
        sa.Column("habilidades_especiais", sa.JSON(), nullable=False),
        sa.Column("anotacoes", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=True),
        sa.Column("atualizado_em", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["combatente_id"], ["combatentes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_familiares_id"), "familiares", ["id"], unique=False)
    op.create_index(
        op.f("ix_familiares_combatente_id"), "familiares", ["combatente_id"], unique=True
    )
    op.create_index(
        op.f("ix_familiares_especie_slug"), "familiares", ["especie_slug"], unique=False
    )


def downgrade() -> None:
    bind = op.get_bind()
    if not _table_exists(bind, "familiares"):
        return
    op.drop_index(op.f("ix_familiares_especie_slug"), table_name="familiares")
    op.drop_index(op.f("ix_familiares_combatente_id"), table_name="familiares")
    op.drop_index(op.f("ix_familiares_id"), table_name="familiares")
    op.drop_table("familiares")
