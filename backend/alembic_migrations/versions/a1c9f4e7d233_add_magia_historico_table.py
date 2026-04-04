"""add_magia_historico_table

Revision ID: a1c9f4e7d233
Revises: f31aa2bc1d55
Create Date: 2026-03-30 23:59:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1c9f4e7d233"
down_revision: Union[str, None] = "f31aa2bc1d55"
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

    if not _table_exists(bind, "magia_historico"):
        op.create_table(
            "magia_historico",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("magia_id", sa.Integer(), nullable=True),
            sa.Column("usuario_id", sa.Integer(), nullable=True),
            sa.Column("acao", sa.String(length=20), nullable=False),
            sa.Column("dados_anteriores", sa.JSON(), nullable=True),
            sa.Column("dados_novos", sa.JSON(), nullable=True),
            sa.Column("criado_em", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists(bind, "magia_historico", "ix_magia_historico_id"):
        op.create_index("ix_magia_historico_id", "magia_historico", ["id"], unique=False)
    if not _index_exists(bind, "magia_historico", "ix_magia_historico_magia_id"):
        op.create_index("ix_magia_historico_magia_id", "magia_historico", ["magia_id"], unique=False)
    if not _index_exists(bind, "magia_historico", "ix_magia_historico_usuario_id"):
        op.create_index("ix_magia_historico_usuario_id", "magia_historico", ["usuario_id"], unique=False)
    if not _index_exists(bind, "magia_historico", "ix_magia_historico_criado_em"):
        op.create_index("ix_magia_historico_criado_em", "magia_historico", ["criado_em"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()

    if _index_exists(bind, "magia_historico", "ix_magia_historico_criado_em"):
        op.drop_index("ix_magia_historico_criado_em", table_name="magia_historico")
    if _index_exists(bind, "magia_historico", "ix_magia_historico_usuario_id"):
        op.drop_index("ix_magia_historico_usuario_id", table_name="magia_historico")
    if _index_exists(bind, "magia_historico", "ix_magia_historico_magia_id"):
        op.drop_index("ix_magia_historico_magia_id", table_name="magia_historico")
    if _index_exists(bind, "magia_historico", "ix_magia_historico_id"):
        op.drop_index("ix_magia_historico_id", table_name="magia_historico")
    if _table_exists(bind, "magia_historico"):
        op.drop_table("magia_historico")
