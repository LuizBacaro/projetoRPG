"""add_combate_historico_table

Revision ID: f2a7b1c4d9e0
Revises: e4a1f9c8d2b3
Create Date: 2026-03-29 00:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f2a7b1c4d9e0"
down_revision: Union[str, None] = "e4a1f9c8d2b3"
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

    if not _table_exists(bind, "combates_historico"):
        op.create_table(
            "combates_historico",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("combate_id", sa.Integer(), nullable=True),
            sa.Column("combatentes_ids", sa.JSON(), nullable=False),
            sa.Column("total_combatentes", sa.Integer(), nullable=False),
            sa.Column("total_vivos", sa.Integer(), nullable=False),
            sa.Column("total_rodadas", sa.Integer(), nullable=False),
            sa.Column("total_turnos", sa.Integer(), nullable=False),
            sa.Column("vencedor_id", sa.Integer(), nullable=True),
            sa.Column("vencedor_nome", sa.String(length=120), nullable=True),
            sa.Column("vencedor_tipo", sa.String(length=20), nullable=True),
            sa.Column("motivo_encerramento", sa.String(length=40), nullable=False),
            sa.Column("estatisticas", sa.JSON(), nullable=False),
            sa.Column("finalizado_em", sa.DateTime(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists(bind, "combates_historico", "ix_combates_historico_id"):
        op.create_index("ix_combates_historico_id", "combates_historico", ["id"], unique=False)
    if not _index_exists(bind, "combates_historico", "ix_combates_historico_combate_id"):
        op.create_index("ix_combates_historico_combate_id", "combates_historico", ["combate_id"], unique=False)
    if not _index_exists(bind, "combates_historico", "ix_combates_historico_finalizado_em"):
        op.create_index("ix_combates_historico_finalizado_em", "combates_historico", ["finalizado_em"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()

    if _index_exists(bind, "combates_historico", "ix_combates_historico_finalizado_em"):
        op.drop_index("ix_combates_historico_finalizado_em", table_name="combates_historico")
    if _index_exists(bind, "combates_historico", "ix_combates_historico_combate_id"):
        op.drop_index("ix_combates_historico_combate_id", table_name="combates_historico")
    if _index_exists(bind, "combates_historico", "ix_combates_historico_id"):
        op.drop_index("ix_combates_historico_id", table_name="combates_historico")
    if _table_exists(bind, "combates_historico"):
        op.drop_table("combates_historico")
