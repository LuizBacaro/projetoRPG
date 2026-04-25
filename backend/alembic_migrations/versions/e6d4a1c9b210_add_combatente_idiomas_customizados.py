"""add_combatente_idiomas_customizados

Revision ID: e6d4a1c9b210
Revises: c2e5a9f14b30
Create Date: 2026-04-25 19:40:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6d4a1c9b210"
down_revision: Union[str, None] = "c2e5a9f14b30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(col.get("name") == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    if not _column_exists(bind, "combatentes", "idiomas_customizados"):
        with op.batch_alter_table("combatentes") as batch_op:
            batch_op.add_column(sa.Column("idiomas_customizados", sa.String(), nullable=True, server_default=""))


def downgrade() -> None:
    bind = op.get_bind()
    if _column_exists(bind, "combatentes", "idiomas_customizados"):
        with op.batch_alter_table("combatentes") as batch_op:
            batch_op.drop_column("idiomas_customizados")
