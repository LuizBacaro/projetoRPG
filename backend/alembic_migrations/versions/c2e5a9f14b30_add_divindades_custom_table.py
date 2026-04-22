"""add_divindades_custom_table

Revision ID: c2e5a9f14b30
Revises: b3c4d5e6f7a8
Create Date: 2026-04-21 21:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c2e5a9f14b30"
down_revision: Union[str, None] = "b3c4d5e6f7a8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, nome: str) -> bool:
    insp = sa.inspect(bind)
    return nome in insp.get_table_names()


def upgrade() -> None:
    """Cria a tabela `divindades_custom` (divindades de campanha)."""
    bind = op.get_bind()
    if _table_exists(bind, "divindades_custom"):
        return

    op.create_table(
        "divindades_custom",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False, server_default=""),
        sa.Column("tendencia", sa.String(length=50), nullable=False),
        sa.Column("dominios", sa.Text(), nullable=False, server_default=""),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column(
            "criado_por_id",
            sa.Integer(),
            sa.ForeignKey("usuarios.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "criado_em",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.UniqueConstraint("nome", name="uq_divindades_custom_nome"),
    )
    op.create_index(
        "ix_divindades_custom_nome",
        "divindades_custom",
        ["nome"],
        unique=False,
    )
    op.create_index(
        "ix_divindades_custom_criado_por_id",
        "divindades_custom",
        ["criado_por_id"],
        unique=False,
    )


def downgrade() -> None:
    """Remove a tabela `divindades_custom`."""
    bind = op.get_bind()
    if not _table_exists(bind, "divindades_custom"):
        return

    try:
        op.drop_index("ix_divindades_custom_criado_por_id", table_name="divindades_custom")
    except Exception:
        pass
    try:
        op.drop_index("ix_divindades_custom_nome", table_name="divindades_custom")
    except Exception:
        pass
    op.drop_table("divindades_custom")
