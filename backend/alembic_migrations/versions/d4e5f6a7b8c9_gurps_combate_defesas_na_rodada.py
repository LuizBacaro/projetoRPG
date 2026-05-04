"""GURPS combate: contagem de defesas por rodada.

Revision ID: d4e5f6a7b8c9
Revises: c9a1b2d3e4f5
Create Date: 2026-05-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, None] = "c9a1b2d3e4f5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tabelas = set(inspector.get_table_names())
    if "gurps_combates" not in tabelas:
        return
    colunas = {c["name"] for c in inspector.get_columns("gurps_combates")}
    if "defesas_na_rodada" in colunas:
        return
    op.add_column("gurps_combates", sa.Column("defesas_na_rodada", sa.JSON(), nullable=True))
    op.execute("UPDATE gurps_combates SET defesas_na_rodada = '{}' WHERE defesas_na_rodada IS NULL")


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tabelas = set(inspector.get_table_names())
    if "gurps_combates" not in tabelas:
        return
    colunas = {c["name"] for c in inspector.get_columns("gurps_combates")}
    if "defesas_na_rodada" not in colunas:
        return
    op.drop_column("gurps_combates", "defesas_na_rodada")

