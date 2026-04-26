"""Adicionar campanhas e vinculo em combatentes.

Revision ID: c1d2e3f4a5b6
Revises: e6d4a1c9b210
Create Date: 2026-04-26
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c1d2e3f4a5b6"
down_revision: Union[str, None] = "e6d4a1c9b210"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if "campanhas" not in inspector.get_table_names():
        op.create_table(
            "campanhas",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("mestre_id", sa.Integer(), nullable=False),
            sa.Column("nome", sa.String(length=120), nullable=False),
            sa.Column("descricao", sa.String(length=500), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
            sa.ForeignKeyConstraint(["mestre_id"], ["usuarios.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_campanhas_id", "campanhas", ["id"], unique=False)
        op.create_index("ix_campanhas_mestre_id", "campanhas", ["mestre_id"], unique=False)

    colunas_combatentes = {col["name"] for col in inspector.get_columns("combatentes")}
    if "campanha_id" not in colunas_combatentes:
        with op.batch_alter_table("combatentes", schema=None) as batch_op:
            batch_op.add_column(sa.Column("campanha_id", sa.Integer(), nullable=True))
            batch_op.create_index("ix_combatentes_campanha_id", ["campanha_id"], unique=False)
            batch_op.create_foreign_key(
                "fk_combatentes_campanha_id_campanhas",
                "campanhas",
                ["campanha_id"],
                ["id"],
            )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    colunas_combatentes = {col["name"] for col in inspector.get_columns("combatentes")}
    if "campanha_id" in colunas_combatentes:
        with op.batch_alter_table("combatentes", schema=None) as batch_op:
            batch_op.drop_constraint("fk_combatentes_campanha_id_campanhas", type_="foreignkey")
            batch_op.drop_index("ix_combatentes_campanha_id")
            batch_op.drop_column("campanha_id")

    if "campanhas" in inspector.get_table_names():
        op.drop_index("ix_campanhas_mestre_id", table_name="campanhas")
        op.drop_index("ix_campanhas_id", table_name="campanhas")
        op.drop_table("campanhas")
