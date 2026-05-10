"""Adicionar coluna secao aos talentos manual

Revision ID: 0bab69d07dc1
Revises: f40738f0b53a
Create Date: 2026-04-18 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0bab69d07dc1'
down_revision: Union[str, None] = 'f40738f0b53a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona coluna secao à tabela talentos."""

    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "talentos" not in insp.get_table_names():
        return
    colunas = {c["name"] for c in insp.get_columns("talentos")}
    if "secao" not in colunas:
        op.add_column("talentos", sa.Column("secao", sa.String(200), nullable=True))


def downgrade() -> None:
    """Remove coluna secao da tabela talentos."""

    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "talentos" not in insp.get_table_names():
        return
    colunas = {c["name"] for c in insp.get_columns("talentos")}
    if "secao" in colunas:
        op.drop_column("talentos", "secao")