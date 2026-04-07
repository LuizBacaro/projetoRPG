"""add_composite_indexes_grimorio_notificacoes

Revision ID: 66fcb1736292
Revises: a5c3f8b2e1d9
Create Date: 2026-04-07 11:45:06.551994

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '66fcb1736292'
down_revision: Union[str, None] = 'a5c3f8b2e1d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        'ix_grimorio_notificacoes_comb_classe_lida',
        'grimorio_notificacoes',
        ['combatente_id', 'classe', 'lida'],
        unique=False,
    )
    op.create_index(
        'ix_grimorio_notificacoes_comb_classe_tipo',
        'grimorio_notificacoes',
        ['combatente_id', 'classe', 'tipo'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index('ix_grimorio_notificacoes_comb_classe_tipo', table_name='grimorio_notificacoes')
    op.drop_index('ix_grimorio_notificacoes_comb_classe_lida', table_name='grimorio_notificacoes')
