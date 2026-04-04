"""add_grimorio_historico_troca_table

Revision ID: ef91a3b2c774
Revises: d21fe43b8aa9
Create Date: 2026-03-30 23:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "ef91a3b2c774"
down_revision: Union[str, None] = "d21fe43b8aa9"
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

    if not _table_exists(bind, "grimorio_historico_troca"):
        op.create_table(
            "grimorio_historico_troca",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("combatente_id", sa.Integer(), nullable=False),
            sa.Column("classe", sa.String(length=50), nullable=False),
            sa.Column("magia_removida_id", sa.Integer(), nullable=False),
            sa.Column("magia_adicionada_id", sa.Integer(), nullable=False),
            sa.Column("nivel_personagem", sa.Integer(), nullable=False),
            sa.Column("realizada_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["combatente_id"], ["combatentes.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["magia_removida_id"], ["magias.id"], ondelete="RESTRICT"),
            sa.ForeignKeyConstraint(["magia_adicionada_id"], ["magias.id"], ondelete="RESTRICT"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists(bind, "grimorio_historico_troca", "ix_grimorio_historico_troca_id"):
        op.create_index("ix_grimorio_historico_troca_id", "grimorio_historico_troca", ["id"], unique=False)
    if not _index_exists(bind, "grimorio_historico_troca", "ix_grimorio_historico_troca_combatente_id"):
        op.create_index("ix_grimorio_historico_troca_combatente_id", "grimorio_historico_troca", ["combatente_id"], unique=False)
    if not _index_exists(bind, "grimorio_historico_troca", "ix_grimorio_historico_troca_classe"):
        op.create_index("ix_grimorio_historico_troca_classe", "grimorio_historico_troca", ["classe"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()

    if _index_exists(bind, "grimorio_historico_troca", "ix_grimorio_historico_troca_classe"):
        op.drop_index("ix_grimorio_historico_troca_classe", table_name="grimorio_historico_troca")
    if _index_exists(bind, "grimorio_historico_troca", "ix_grimorio_historico_troca_combatente_id"):
        op.drop_index("ix_grimorio_historico_troca_combatente_id", table_name="grimorio_historico_troca")
    if _index_exists(bind, "grimorio_historico_troca", "ix_grimorio_historico_troca_id"):
        op.drop_index("ix_grimorio_historico_troca_id", table_name="grimorio_historico_troca")
    if _table_exists(bind, "grimorio_historico_troca"):
        op.drop_table("grimorio_historico_troca")
