"""add_grimorio_notificacoes_table

Revision ID: f31aa2bc1d55
Revises: ef91a3b2c774
Create Date: 2026-03-30 23:55:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "f31aa2bc1d55"
down_revision: Union[str, None] = "ef91a3b2c774"
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

    if not _table_exists(bind, "grimorio_notificacoes"):
        op.create_table(
            "grimorio_notificacoes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("combatente_id", sa.Integer(), nullable=False),
            sa.Column("classe", sa.String(length=50), nullable=False),
            sa.Column("tipo", sa.String(length=40), nullable=False),
            sa.Column("dados", sa.Text(), nullable=True),
            sa.Column("lida", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("criada_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["combatente_id"], ["combatentes.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists(bind, "grimorio_notificacoes", "ix_grimorio_notificacoes_id"):
        op.create_index("ix_grimorio_notificacoes_id", "grimorio_notificacoes", ["id"], unique=False)
    if not _index_exists(bind, "grimorio_notificacoes", "ix_grimorio_notificacoes_combatente_id"):
        op.create_index(
            "ix_grimorio_notificacoes_combatente_id",
            "grimorio_notificacoes",
            ["combatente_id"],
            unique=False,
        )
    if not _index_exists(bind, "grimorio_notificacoes", "ix_grimorio_notificacoes_classe"):
        op.create_index("ix_grimorio_notificacoes_classe", "grimorio_notificacoes", ["classe"], unique=False)
    if not _index_exists(bind, "grimorio_notificacoes", "ix_grimorio_notificacoes_tipo"):
        op.create_index("ix_grimorio_notificacoes_tipo", "grimorio_notificacoes", ["tipo"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()

    if _index_exists(bind, "grimorio_notificacoes", "ix_grimorio_notificacoes_tipo"):
        op.drop_index("ix_grimorio_notificacoes_tipo", table_name="grimorio_notificacoes")
    if _index_exists(bind, "grimorio_notificacoes", "ix_grimorio_notificacoes_classe"):
        op.drop_index("ix_grimorio_notificacoes_classe", table_name="grimorio_notificacoes")
    if _index_exists(bind, "grimorio_notificacoes", "ix_grimorio_notificacoes_combatente_id"):
        op.drop_index("ix_grimorio_notificacoes_combatente_id", table_name="grimorio_notificacoes")
    if _index_exists(bind, "grimorio_notificacoes", "ix_grimorio_notificacoes_id"):
        op.drop_index("ix_grimorio_notificacoes_id", table_name="grimorio_notificacoes")
    if _table_exists(bind, "grimorio_notificacoes"):
        op.drop_table("grimorio_notificacoes")
