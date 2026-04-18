"""Adicionar campos equipamentos manual

Revision ID: af4a62e567b7
Revises: 173c62f6aa14
Create Date: 2026-04-18 08:15:07.566810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af4a62e567b7'
down_revision: Union[str, None] = '874ba656c7c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona novos campos à tabela equipamentos."""
    
    # Listar campos a adicionar
    campos = [
        ('categoria', sa.String(50)),
        ('subcategoria', sa.String(100)),
        ('custo', sa.String(50)),
        ('dano_pequeno', sa.String(20)),
        ('dano_medio', sa.String(20)),
        ('critico', sa.String(20)),
        ('alcance_incremento', sa.String(50)),
        ('peso', sa.String(20)),
        ('tipo_dano', sa.String(50)),
    ]
    
    # Adicionar cada coluna
    # SQLite e PostgreSQL lidam com "coluna já existe" de formas diferentes
    # Por isso fazemos um try/except por coluna
    for nome_campo, tipo in campos:
        try:
            op.add_column('equipamentos', sa.Column(nome_campo, tipo, nullable=True))
        except Exception as e:
            # Silenciar erros "coluna já existe" - compatível com SQLite e PostgreSQL
            erro_str = str(e).lower()
            if "duplicate column" in erro_str or "already exists" in erro_str:
                pass  # Coluna já existe, tudo bem
            else:
                raise  # Re-raise se for outro tipo de erro


def downgrade() -> None:
    """Remove novos campos da tabela equipamentos."""
    
    # Campos a remover (na ordem inversa)
    campos_remover = [
        'tipo_dano',
        'peso',
        'alcance_incremento',
        'critico',
        'dano_medio',
        'dano_pequeno',
        'custo',
        'subcategoria',
        'categoria',
    ]
    
    for nome_campo in campos_remover:
        try:
            op.drop_column('equipamentos', nome_campo)
        except Exception as e:
            # Silenciar erros "coluna não existe"
            erro_str = str(e).lower()
            if "no such column" in erro_str or "does not exist" in erro_str:
                pass  # Coluna não existe, tudo bem
            else:
                raise  # Re-raise se for outro tipo de erro
