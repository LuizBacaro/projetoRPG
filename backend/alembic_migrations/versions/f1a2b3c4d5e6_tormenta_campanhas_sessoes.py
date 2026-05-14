"""Tormenta 20 — campanhas, sessões e FK em personagens.

Revision ID: f1a2b3c4d5e6
Revises: b4d6e8f0a2c1
Create Date: 2026-05-11
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import inspect

revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, None] = "b4d6e8f0a2c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tabelas = insp.get_table_names()

    if "tormenta_campanhas" not in tabelas:
        op.create_table(
            "tormenta_campanhas",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("mestre_id", sa.Integer(), nullable=False),
            sa.Column("nome", sa.String(length=120), nullable=False),
            sa.Column("descricao", sa.String(length=500), nullable=True),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(["mestre_id"], ["usuarios.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_tormenta_campanhas_mestre_id",
            "tormenta_campanhas",
            ["mestre_id"],
            unique=False,
        )
        op.create_index(
            "ix_tormenta_campanhas_id", "tormenta_campanhas", ["id"], unique=False
        )

    if "tormenta_campanhas_sessoes" not in tabelas:
        op.create_table(
            "tormenta_campanhas_sessoes",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("campanha_id", sa.Integer(), nullable=False),
            sa.Column("resumo", sa.String(length=4000), nullable=False),
            sa.Column(
                "visivel_jogadores",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
            ),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.ForeignKeyConstraint(
                ["campanha_id"],
                ["tormenta_campanhas.id"],
                ondelete="CASCADE",
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(
            "ix_tormenta_campanhas_sessoes_id",
            "tormenta_campanhas_sessoes",
            ["id"],
            unique=False,
        )
        op.create_index(
            "ix_tormenta_campanhas_sessoes_campanha_id",
            "tormenta_campanhas_sessoes",
            ["campanha_id"],
            unique=False,
        )

    cols = {c["name"] for c in insp.get_columns("tormenta_personagens")}
    if "campanha_id" not in cols:
        op.add_column(
            "tormenta_personagens",
            sa.Column("campanha_id", sa.Integer(), nullable=True),
        )
        op.create_index(
            "ix_tormenta_personagens_campanha_id",
            "tormenta_personagens",
            ["campanha_id"],
            unique=False,
        )
        op.create_foreign_key(
            "fk_tormenta_personagens_campanha_id",
            "tormenta_personagens",
            "tormenta_campanhas",
            ["campanha_id"],
            ["id"],
            ondelete="SET NULL",
        )


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tabelas = insp.get_table_names()
    cols = (
        {c["name"] for c in insp.get_columns("tormenta_personagens")}
        if "tormenta_personagens" in tabelas
        else set()
    )
    if "campanha_id" in cols:
        op.drop_constraint(
            "fk_tormenta_personagens_campanha_id",
            "tormenta_personagens",
            type_="foreignkey",
        )
        op.drop_index("ix_tormenta_personagens_campanha_id", table_name="tormenta_personagens")
        op.drop_column("tormenta_personagens", "campanha_id")
    if "tormenta_campanhas_sessoes" in tabelas:
        op.drop_index(
            "ix_tormenta_campanhas_sessoes_campanha_id",
            table_name="tormenta_campanhas_sessoes",
        )
        op.drop_index(
            "ix_tormenta_campanhas_sessoes_id", table_name="tormenta_campanhas_sessoes"
        )
        op.drop_table("tormenta_campanhas_sessoes")
    if "tormenta_campanhas" in tabelas:
        op.drop_index("ix_tormenta_campanhas_id", table_name="tormenta_campanhas")
        op.drop_index("ix_tormenta_campanhas_mestre_id", table_name="tormenta_campanhas")
        op.drop_table("tormenta_campanhas")
