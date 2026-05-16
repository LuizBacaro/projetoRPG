"""Tabelas tormenta_talentos e tormenta_talentos_personagem (catálogo + vínculo).

Revision ID: b9c8d7e6f5a4
Revises: f0a1b2c3d4e5
Create Date: 2026-05-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b9c8d7e6f5a4"
down_revision: Union[str, None] = "f0a1b2c3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tormenta_talentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("pagina_referencia", sa.String(length=50), nullable=True),
        sa.Column(
            "origem_catalogo_mb",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", name="uq_tormenta_talentos_nome"),
    )
    op.create_index("ix_tormenta_talentos_id", "tormenta_talentos", ["id"], unique=False)
    op.create_index("ix_tormenta_talentos_nome", "tormenta_talentos", ["nome"], unique=False)

    op.create_table(
        "tormenta_talentos_personagem",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("talento_id", sa.Integer(), nullable=False),
        sa.Column("notas", sa.String(length=500), nullable=True),
        sa.Column("adicionado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["personagem_id"],
            ["tormenta_personagens.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["talento_id"],
            ["tormenta_talentos.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "personagem_id",
            "talento_id",
            name="uq_tormenta_talento_personagem_par",
        ),
    )
    op.create_index(
        "ix_tormenta_talentos_personagem_id",
        "tormenta_talentos_personagem",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_tormenta_talentos_personagem_personagem_id",
        "tormenta_talentos_personagem",
        ["personagem_id"],
        unique=False,
    )
    op.create_index(
        "ix_tormenta_talentos_personagem_talento_id",
        "tormenta_talentos_personagem",
        ["talento_id"],
        unique=False,
    )

    from datetime import datetime, timezone

    from sqlalchemy.sql import column, table

    from app.games.tormenta.rules.catalogo_t20 import lista_talentos_mb_catalogo

    now = datetime.now(timezone.utc)
    rows = []
    for r in lista_talentos_mb_catalogo():
        nome = str(r.get("nome", "")).strip()[:200]
        if not nome:
            continue
        rows.append(
            {
                "nome": nome,
                "descricao": None,
                "pagina_referencia": None,
                "origem_catalogo_mb": True,
                "criado_em": now,
            }
        )
    if rows:
        tal_tbl = table(
            "tormenta_talentos",
            column("nome", sa.String(200)),
            column("descricao", sa.Text()),
            column("pagina_referencia", sa.String(50)),
            column("origem_catalogo_mb", sa.Boolean()),
            column("criado_em", sa.DateTime()),
        )
        op.bulk_insert(tal_tbl, rows)


def downgrade() -> None:
    op.drop_index(
        "ix_tormenta_talentos_personagem_talento_id",
        table_name="tormenta_talentos_personagem",
    )
    op.drop_index(
        "ix_tormenta_talentos_personagem_personagem_id",
        table_name="tormenta_talentos_personagem",
    )
    op.drop_index(
        "ix_tormenta_talentos_personagem_id",
        table_name="tormenta_talentos_personagem",
    )
    op.drop_table("tormenta_talentos_personagem")
    op.drop_index("ix_tormenta_talentos_nome", table_name="tormenta_talentos")
    op.drop_index("ix_tormenta_talentos_id", table_name="tormenta_talentos")
    op.drop_table("tormenta_talentos")
