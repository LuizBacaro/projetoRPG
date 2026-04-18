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
    # Adicionar novos campos à tabela equipamentos
    op.add_column('equipamentos', sa.Column('categoria', sa.String(50), nullable=True))
    op.add_column('equipamentos', sa.Column('subcategoria', sa.String(100), nullable=True))
    op.add_column('equipamentos', sa.Column('custo', sa.String(50), nullable=True))
    op.add_column('equipamentos', sa.Column('dano_pequeno', sa.String(20), nullable=True))
    op.add_column('equipamentos', sa.Column('dano_medio', sa.String(20), nullable=True))
    op.add_column('equipamentos', sa.Column('critico', sa.String(20), nullable=True))
    op.add_column('equipamentos', sa.Column('alcance_incremento', sa.String(50), nullable=True))
    op.add_column('equipamentos', sa.Column('peso', sa.String(20), nullable=True))
    op.add_column('equipamentos', sa.Column('tipo_dano', sa.String(50), nullable=True))


def downgrade() -> None:
    # Remover novos campos da tabela equipamentos
    op.drop_column('equipamentos', 'tipo_dano')
    op.drop_column('equipamentos', 'peso')
    op.drop_column('equipamentos', 'alcance_incremento')
    op.drop_column('equipamentos', 'critico')
    op.drop_column('equipamentos', 'dano_medio')
    op.drop_column('equipamentos', 'dano_pequeno')
    op.drop_column('equipamentos', 'custo')
    op.drop_column('equipamentos', 'subcategoria')
    op.drop_column('equipamentos', 'categoria')
