"""add_prerequisitos_secao_to_talentos

Revision ID: a1b2c3d4e5f6
Revises: e4a1f9c8d2b3
Create Date: 2026-04-17 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, None] = "e4a1f9c8d2b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _coluna_existe(tabela: str, coluna: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    colunas = [c["name"] for c in inspector.get_columns(tabela)]
    return coluna in colunas


def upgrade() -> None:
    # Adicionar coluna prerequisitos
    if not _coluna_existe("talentos", "prerequisitos"):
        op.add_column(
            "talentos",
            sa.Column("prerequisitos", sa.String(500), nullable=True)
        )
    
    # Adicionar coluna secao
    if not _coluna_existe("talentos", "secao"):
        op.add_column(
            "talentos",
            sa.Column("secao", sa.String(100), nullable=True)
        )


def downgrade() -> None:
    # Remover colunas em caso de rollback
    if _coluna_existe("talentos", "secao"):
        op.drop_column("talentos", "secao")
    
    if _coluna_existe("talentos", "prerequisitos"):
        op.drop_column("talentos", "prerequisitos")
