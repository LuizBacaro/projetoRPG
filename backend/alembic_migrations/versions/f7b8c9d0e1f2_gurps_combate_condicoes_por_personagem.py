"""GURPS combate: estado de condições por personagem.

Revision ID: f7b8c9d0e1f2
Revises: e5f6a7b8c9d0
Create Date: 2026-05-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision: str = "f7b8c9d0e1f2"
down_revision: Union[str, None] = "e5f6a7b8c9d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tabelas = set(inspector.get_table_names())
    if "gurps_combates" not in tabelas:
        return
    colunas = {c["name"] for c in inspector.get_columns("gurps_combates")}
    if "condicoes_por_personagem" in colunas:
        return
    op.add_column(
        "gurps_combates",
        sa.Column("condicoes_por_personagem", sa.JSON(), nullable=True),
    )
    op.execute(
        "UPDATE gurps_combates SET condicoes_por_personagem = '{}' WHERE condicoes_por_personagem IS NULL"
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    tabelas = set(inspector.get_table_names())
    if "gurps_combates" not in tabelas:
        return
    colunas = {c["name"] for c in inspector.get_columns("gurps_combates")}
    if "condicoes_por_personagem" not in colunas:
        return
    op.drop_column("gurps_combates", "condicoes_por_personagem")

