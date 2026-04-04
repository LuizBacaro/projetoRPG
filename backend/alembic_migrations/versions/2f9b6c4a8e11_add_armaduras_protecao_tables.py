"""add_armaduras_protecao_tables

Revision ID: 2f9b6c4a8e11
Revises: f31aa2bc1d55
Create Date: 2026-04-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "2f9b6c4a8e11"
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

    if not _table_exists(bind, "armaduras_protecao"):
        op.create_table(
            "armaduras_protecao",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("nome", sa.String(length=120), nullable=False),
            sa.Column("tipo", sa.String(length=60), nullable=False),
            sa.Column("bonus_ca", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("des_max", sa.String(length=20), nullable=True),
            sa.Column("penalidade", sa.Integer(), nullable=False, server_default=sa.text("0")),
            sa.Column("falha_arcana", sa.String(length=20), nullable=True),
            sa.Column("deslocamento", sa.String(length=40), nullable=True),
            sa.Column("peso", sa.Float(), nullable=True),
            sa.Column("propriedades_especiais", sa.String(length=600), nullable=True),
            sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("criado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists(bind, "armaduras_protecao", "ix_armaduras_protecao_id"):
        op.create_index("ix_armaduras_protecao_id", "armaduras_protecao", ["id"], unique=False)
    if not _index_exists(bind, "armaduras_protecao", "ix_armaduras_protecao_nome"):
        op.create_index("ix_armaduras_protecao_nome", "armaduras_protecao", ["nome"], unique=False)
    if not _index_exists(bind, "armaduras_protecao", "ix_armaduras_protecao_ativo"):
        op.create_index("ix_armaduras_protecao_ativo", "armaduras_protecao", ["ativo"], unique=False)

    if not _table_exists(bind, "armaduras_protecao_jogador"):
        op.create_table(
            "armaduras_protecao_jogador",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("combatente_id", sa.Integer(), nullable=False),
            sa.Column("item_id", sa.Integer(), nullable=False),
            sa.Column("adicionado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
            sa.ForeignKeyConstraint(["combatente_id"], ["combatentes.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["item_id"], ["armaduras_protecao.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _index_exists(bind, "armaduras_protecao_jogador", "ix_armaduras_protecao_jogador_id"):
        op.create_index("ix_armaduras_protecao_jogador_id", "armaduras_protecao_jogador", ["id"], unique=False)
    if not _index_exists(bind, "armaduras_protecao_jogador", "ix_armaduras_protecao_jogador_combatente_id"):
        op.create_index(
            "ix_armaduras_protecao_jogador_combatente_id",
            "armaduras_protecao_jogador",
            ["combatente_id"],
            unique=False,
        )
    if not _index_exists(bind, "armaduras_protecao_jogador", "ix_armaduras_protecao_jogador_item_id"):
        op.create_index(
            "ix_armaduras_protecao_jogador_item_id",
            "armaduras_protecao_jogador",
            ["item_id"],
            unique=False,
        )


def downgrade() -> None:
    bind = op.get_bind()

    if _index_exists(bind, "armaduras_protecao_jogador", "ix_armaduras_protecao_jogador_item_id"):
        op.drop_index("ix_armaduras_protecao_jogador_item_id", table_name="armaduras_protecao_jogador")
    if _index_exists(bind, "armaduras_protecao_jogador", "ix_armaduras_protecao_jogador_combatente_id"):
        op.drop_index("ix_armaduras_protecao_jogador_combatente_id", table_name="armaduras_protecao_jogador")
    if _index_exists(bind, "armaduras_protecao_jogador", "ix_armaduras_protecao_jogador_id"):
        op.drop_index("ix_armaduras_protecao_jogador_id", table_name="armaduras_protecao_jogador")
    if _table_exists(bind, "armaduras_protecao_jogador"):
        op.drop_table("armaduras_protecao_jogador")

    if _index_exists(bind, "armaduras_protecao", "ix_armaduras_protecao_ativo"):
        op.drop_index("ix_armaduras_protecao_ativo", table_name="armaduras_protecao")
    if _index_exists(bind, "armaduras_protecao", "ix_armaduras_protecao_nome"):
        op.drop_index("ix_armaduras_protecao_nome", table_name="armaduras_protecao")
    if _index_exists(bind, "armaduras_protecao", "ix_armaduras_protecao_id"):
        op.drop_index("ix_armaduras_protecao_id", table_name="armaduras_protecao")
    if _table_exists(bind, "armaduras_protecao"):
        op.drop_table("armaduras_protecao")
