"""Adicionar coluna prerequisitos aos talentos manual

Revision ID: f40738f0b53a
Revises: af4a62e567b7
Create Date: 2026-04-18 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f40738f0b53a'
down_revision: Union[str, None] = 'af4a62e567b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona colunas prerequisitos e secao à tabela talentos."""

    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "talentos" not in insp.get_table_names():
        return
    colunas = {c["name"] for c in insp.get_columns("talentos")}

    # Postgres: erro em add_column aborta a transação — não usar try/except por coluna.
    if "prerequisitos" not in colunas:
        op.add_column(
            "talentos", sa.Column("prerequisitos", sa.String(500), nullable=True)
        )
    if "secao" not in colunas:
        op.add_column("talentos", sa.Column("secao", sa.String(200), nullable=True))


def downgrade() -> None:
    """Remove colunas prerequisitos e secao da tabela talentos."""

    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "talentos" not in insp.get_table_names():
        return
    colunas = {c["name"] for c in insp.get_columns("talentos")}

    if "secao" in colunas:
        op.drop_column("talentos", "secao")
    if "prerequisitos" in colunas:
        op.drop_column("talentos", "prerequisitos")