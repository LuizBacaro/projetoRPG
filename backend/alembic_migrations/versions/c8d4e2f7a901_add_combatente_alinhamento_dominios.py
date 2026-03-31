"""add_combatente_alinhamento_dominios

Revision ID: c8d4e2f7a901
Revises: a1c9f4e7d233
Create Date: 2026-03-31 00:20:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c8d4e2f7a901"
down_revision: Union[str, None] = "a1c9f4e7d233"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
	inspector = sa.inspect(bind)
	if table_name not in inspector.get_table_names():
		return False
	return any(col.get("name") == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
	bind = op.get_bind()

	if not _column_exists(bind, "combatentes", "alinhamento"):
		with op.batch_alter_table("combatentes") as batch_op:
			batch_op.add_column(sa.Column("alinhamento", sa.String(), nullable=True, server_default=""))

	if not _column_exists(bind, "combatentes", "dominios"):
		with op.batch_alter_table("combatentes") as batch_op:
			batch_op.add_column(sa.Column("dominios", sa.String(), nullable=True, server_default=""))


def downgrade() -> None:
	bind = op.get_bind()

	if _column_exists(bind, "combatentes", "dominios"):
		with op.batch_alter_table("combatentes") as batch_op:
			batch_op.drop_column("dominios")

	if _column_exists(bind, "combatentes", "alinhamento"):
		with op.batch_alter_table("combatentes") as batch_op:
			batch_op.drop_column("alinhamento")
