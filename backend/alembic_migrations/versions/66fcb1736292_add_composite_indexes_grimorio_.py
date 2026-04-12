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


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(idx.get("name") == index_name for idx in inspector.get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, 'grimorio_notificacoes') and not _index_exists(
        bind,
        'grimorio_notificacoes',
        'ix_grimorio_notificacoes_comb_classe_lida',
    ):
        op.create_index(
            'ix_grimorio_notificacoes_comb_classe_lida',
            'grimorio_notificacoes',
            ['combatente_id', 'classe', 'lida'],
            unique=False,
        )

    if _table_exists(bind, 'grimorio_notificacoes') and not _index_exists(
        bind,
        'grimorio_notificacoes',
        'ix_grimorio_notificacoes_comb_classe_tipo',
    ):
        op.create_index(
            'ix_grimorio_notificacoes_comb_classe_tipo',
            'grimorio_notificacoes',
            ['combatente_id', 'classe', 'tipo'],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if _index_exists(bind, 'grimorio_notificacoes', 'ix_grimorio_notificacoes_comb_classe_tipo'):
        op.drop_index('ix_grimorio_notificacoes_comb_classe_tipo', table_name='grimorio_notificacoes')
    if _index_exists(bind, 'grimorio_notificacoes', 'ix_grimorio_notificacoes_comb_classe_lida'):
        op.drop_index('ix_grimorio_notificacoes_comb_classe_lida', table_name='grimorio_notificacoes')
