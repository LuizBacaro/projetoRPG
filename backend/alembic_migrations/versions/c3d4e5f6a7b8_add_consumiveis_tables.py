"""add_consumiveis_tables

Revision ID: c3d4e5f6a7b8
Revises: fase_c_schemas_auth_dnd35
Create Date: 2026-04-30 07:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, None] = "fase_c_schemas_auth_dnd35"
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

    if not _table_exists(bind, "consumiveis"):
        op.create_table(
            "consumiveis",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("nome", sa.String(length=120), nullable=False),
            sa.Column("descricao", sa.String(length=600), nullable=True),
            sa.Column("pagina_referencia", sa.String(length=50), nullable=True),
            sa.Column("categoria", sa.String(length=60), nullable=True),
            sa.Column("tipo", sa.String(length=60), nullable=True),
            sa.Column("custo", sa.String(length=50), nullable=True),
            sa.Column("peso", sa.String(length=30), nullable=True),
            sa.Column("criado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("deleted_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists(bind, "consumiveis", "ix_consumiveis_id"):
        op.create_index("ix_consumiveis_id", "consumiveis", ["id"], unique=False)
    if not _index_exists(bind, "consumiveis", "ix_consumiveis_nome"):
        op.create_index("ix_consumiveis_nome", "consumiveis", ["nome"], unique=False)
    if not _index_exists(bind, "consumiveis", "ix_consumiveis_ativo"):
        op.create_index("ix_consumiveis_ativo", "consumiveis", ["ativo"], unique=False)

    if not _table_exists(bind, "consumiveis_jogador"):
        op.create_table(
            "consumiveis_jogador",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("combatente_id", sa.Integer(), nullable=False),
            sa.Column("consumivel_id", sa.Integer(), nullable=False),
            sa.Column("quantidade", sa.Integer(), nullable=False, server_default=sa.text("1")),
            sa.Column("adicionado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["combatente_id"], ["combatentes.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["consumivel_id"], ["consumiveis.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists(bind, "consumiveis_jogador", "ix_consumiveis_jogador_id"):
        op.create_index("ix_consumiveis_jogador_id", "consumiveis_jogador", ["id"], unique=False)
    if not _index_exists(bind, "consumiveis_jogador", "ix_consumiveis_jogador_combatente_id"):
        op.create_index(
            "ix_consumiveis_jogador_combatente_id",
            "consumiveis_jogador",
            ["combatente_id"],
            unique=False,
        )
    if not _index_exists(bind, "consumiveis_jogador", "ix_consumiveis_jogador_consumivel_id"):
        op.create_index(
            "ix_consumiveis_jogador_consumivel_id",
            "consumiveis_jogador",
            ["consumivel_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "consumiveis_jogador"):
        op.drop_table("consumiveis_jogador")
    if _table_exists(bind, "consumiveis"):
        op.drop_table("consumiveis")
