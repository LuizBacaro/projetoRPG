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
    
    # Adicionar coluna secao
    try:
        op.add_column('talentos', sa.Column('secao', sa.String(200), nullable=True))
    except Exception as e:
        # Silenciar erros "coluna já existe" - compatível com SQLite e PostgreSQL
        erro_str = str(e).lower()
        if "duplicate column" in erro_str or "already exists" in erro_str:
            pass  # Coluna já existe, tudo bem
        else:
            raise  # Re-raise se for outro tipo de erro


def downgrade() -> None:
    """Remove coluna secao da tabela talentos."""
    
    # Remover coluna secao
    try:
        op.drop_column('talentos', 'secao')
    except Exception as e:
        # Silenciar erros se a coluna não existir
        erro_str = str(e).lower()
        if "no such column" in erro_str or "does not exist" in erro_str:
            pass  # Coluna não existe, tudo bem
        else:
            raise  # Re-raise se for outro tipo de erro