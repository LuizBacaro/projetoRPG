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
    
    # Adicionar coluna prerequisitos
    try:
        op.add_column('talentos', sa.Column('prerequisitos', sa.String(500), nullable=True))
    except Exception as e:
        # Silenciar erros "coluna já existe" - compatível com SQLite e PostgreSQL
        erro_str = str(e).lower()
        if "duplicate column" in erro_str or "already exists" in erro_str:
            pass  # Coluna já existe, tudo bem
        else:
            raise  # Re-raise se for outro tipo de erro
    
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
    """Remove colunas prerequisitos e secao da tabela talentos."""
    
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
    
    # Remover coluna prerequisitos
    try:
        op.drop_column('talentos', 'prerequisitos')
    except Exception as e:
        # Silenciar erros se a coluna não existir
        erro_str = str(e).lower()
        if "no such column" in erro_str or "does not exist" in erro_str:
            pass  # Coluna não existe, tudo bem
        else:
            raise  # Re-raise se for outro tipo de erro