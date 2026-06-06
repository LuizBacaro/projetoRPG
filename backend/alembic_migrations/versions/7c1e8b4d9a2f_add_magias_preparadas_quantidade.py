"""add_magias_preparadas_quantidade

Revision ID: 7c1e8b4d9a2f
Revises: a1c9f4e7d233
Create Date: 2026-04-01 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c1e8b4d9a2f"
down_revision: Union[str, None] = "a1c9f4e7d233"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _coluna_existe(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(col.get("name") == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    if "magias_preparadas" not in sa.inspect(bind).get_table_names():
        return

    with op.batch_alter_table("magias_preparadas") as batch_op:
        if not _coluna_existe(bind, "magias_preparadas", "quantidade"):
            batch_op.add_column(sa.Column("quantidade", sa.Integer(), nullable=False, server_default="1"))
        if not _coluna_existe(bind, "magias_preparadas", "usos_realizados"):
            batch_op.add_column(sa.Column("usos_realizados", sa.Integer(), nullable=False, server_default="0"))

    op.execute("UPDATE magias_preparadas SET quantidade = 1 WHERE quantidade IS NULL OR quantidade < 1")
    op.execute("UPDATE magias_preparadas SET usos_realizados = 0 WHERE usos_realizados IS NULL OR usos_realizados < 0")


def downgrade() -> None:
    bind = op.get_bind()
    if "magias_preparadas" not in sa.inspect(bind).get_table_names():
        return

    with op.batch_alter_table("magias_preparadas") as batch_op:
        if _coluna_existe(bind, "magias_preparadas", "usos_realizados"):
            batch_op.drop_column("usos_realizados")
        if _coluna_existe(bind, "magias_preparadas", "quantidade"):
            batch_op.drop_column("quantidade")
