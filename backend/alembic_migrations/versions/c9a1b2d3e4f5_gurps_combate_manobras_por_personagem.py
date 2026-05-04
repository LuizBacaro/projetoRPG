"""GURPS combate: estado de manobra por personagem.

Revision ID: c9a1b2d3e4f5
Revises: f7a8b9c0d1e2
Create Date: 2026-05-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "c9a1b2d3e4f5"
down_revision: Union[str, None] = "f7a8b9c0d1e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tabelas = set(inspector.get_table_names())
    if "gurps_combates" not in tabelas:
        return
    colunas = {c["name"] for c in inspector.get_columns("gurps_combates")}
    if "manobras_por_personagem" in colunas:
        return

    op.add_column(
        "gurps_combates",
        sa.Column("manobras_por_personagem", sa.JSON(), nullable=True),
    )
    op.execute("UPDATE gurps_combates SET manobras_por_personagem = '{}' WHERE manobras_por_personagem IS NULL")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tabelas = set(inspector.get_table_names())
    if "gurps_combates" not in tabelas:
        return
    colunas = {c["name"] for c in inspector.get_columns("gurps_combates")}
    if "manobras_por_personagem" not in colunas:
        return
    op.drop_column("gurps_combates", "manobras_por_personagem")

