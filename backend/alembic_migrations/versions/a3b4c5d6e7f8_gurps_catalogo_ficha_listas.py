"""GURPS: catálogo da ficha (vantagens, desvantagens, perícias) em tabelas opcionais.

Revision ID: a3b4c5d6e7f8
Revises: f7b8c9d0e1f2
Create Date: 2026-05-04
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a3b4c5d6e7f8"
down_revision: Union[str, None] = "f7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gurps_catalogo_ficha_vantagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=512), nullable=False),
        sa.Column("custo", sa.Integer(), nullable=True),
        sa.Column("custo_texto", sa.String(length=255), nullable=True),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", name="uq_gurps_cat_ficha_vant_nome"),
    )
    op.create_index(
        "ix_gurps_cat_ficha_vant_ordem",
        "gurps_catalogo_ficha_vantagens",
        ["ordem"],
        unique=False,
    )

    op.create_table(
        "gurps_catalogo_ficha_desvantagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=512), nullable=False),
        sa.Column("custo", sa.Integer(), nullable=True),
        sa.Column("custo_texto", sa.String(length=255), nullable=True),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", name="uq_gurps_cat_ficha_desv_nome"),
    )
    op.create_index(
        "ix_gurps_cat_ficha_desv_ordem",
        "gurps_catalogo_ficha_desvantagens",
        ["ordem"],
        unique=False,
    )

    op.create_table(
        "gurps_catalogo_ficha_pericias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=512), nullable=False),
        sa.Column("atributo_base", sa.String(length=16), nullable=False, server_default="dx"),
        sa.Column("dificuldade", sa.String(length=8), nullable=False, server_default="M"),
        sa.Column("nt", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", name="uq_gurps_cat_ficha_per_nome"),
    )
    op.create_index(
        "ix_gurps_cat_ficha_per_ordem",
        "gurps_catalogo_ficha_pericias",
        ["ordem"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_gurps_cat_ficha_per_ordem", table_name="gurps_catalogo_ficha_pericias")
    op.drop_table("gurps_catalogo_ficha_pericias")
    op.drop_index("ix_gurps_cat_ficha_desv_ordem", table_name="gurps_catalogo_ficha_desvantagens")
    op.drop_table("gurps_catalogo_ficha_desvantagens")
    op.drop_index("ix_gurps_cat_ficha_vant_ordem", table_name="gurps_catalogo_ficha_vantagens")
    op.drop_table("gurps_catalogo_ficha_vantagens")
