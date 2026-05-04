"""GURPS combate: estado de postura por personagem.

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-05-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tabelas = set(inspector.get_table_names())
    if "gurps_combates" not in tabelas:
        return
    colunas = {c["name"] for c in inspector.get_columns("gurps_combates")}
    if "posturas_por_personagem" in colunas:
        return
    op.add_column(
        "gurps_combates",
        sa.Column("posturas_por_personagem", sa.JSON(), nullable=True),
    )
    op.execute(
        "UPDATE gurps_combates SET posturas_por_personagem = '{}' WHERE posturas_por_personagem IS NULL"
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tabelas = set(inspector.get_table_names())
    if "gurps_combates" not in tabelas:
        return
    colunas = {c["name"] for c in inspector.get_columns("gurps_combates")}
    if "posturas_por_personagem" not in colunas:
        return
    op.drop_column("gurps_combates", "posturas_por_personagem")

