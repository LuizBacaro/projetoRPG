"""vinculos_arena_combatente_id

Revision ID: d7e8f9a0b1c2
Revises: c9d8e7f6a5b4
Create Date: 2026-05-17 18:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d7e8f9a0b1c2"
down_revision: Union[str, None] = "c9d8e7f6a5b4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(bind, table: str, column: str) -> bool:
    inspector = sa.inspect(bind)
    cols = [c["name"] for c in inspector.get_columns(table)]
    return column in cols


def upgrade() -> None:
    bind = op.get_bind()
    for table in ("companheiros_animais", "familiares"):
        if not _column_exists(bind, table, "arena_combatente_id"):
            op.add_column(
                table,
                sa.Column("arena_combatente_id", sa.Integer(), nullable=True),
            )
            op.create_foreign_key(
                f"fk_{table}_arena_combatente_id",
                table,
                "combatentes",
                ["arena_combatente_id"],
                ["id"],
                ondelete="SET NULL",
            )
            op.create_index(
                op.f(f"ix_{table}_arena_combatente_id"),
                table,
                ["arena_combatente_id"],
                unique=False,
            )


def downgrade() -> None:
    bind = op.get_bind()
    for table in ("familiares", "companheiros_animais"):
        if _column_exists(bind, table, "arena_combatente_id"):
            op.drop_index(op.f(f"ix_{table}_arena_combatente_id"), table_name=table)
            op.drop_constraint(
                f"fk_{table}_arena_combatente_id", table, type_="foreignkey"
            )
            op.drop_column(table, "arena_combatente_id")
