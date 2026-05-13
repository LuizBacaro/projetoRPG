"""Tabelas tormenta_equipamentos / tormenta_consumiveis e vínculos ao personagem.

Revision ID: c0d1e2f3a4b6
Revises: b9c8d7e6f5a4
Create Date: 2026-05-13
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c0d1e2f3a4b6"
down_revision: Union[str, None] = "b9c8d7e6f5a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tormenta_equipamentos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("categoria", sa.String(length=120), nullable=True),
        sa.Column("secao", sa.String(length=200), nullable=True),
        sa.Column("custo", sa.String(length=80), nullable=True),
        sa.Column("dano_p", sa.String(length=40), nullable=True),
        sa.Column("dano_m", sa.String(length=40), nullable=True),
        sa.Column("tipo_dano", sa.String(length=120), nullable=True),
        sa.Column("critico", sa.String(length=80), nullable=True),
        sa.Column("alcance", sa.String(length=80), nullable=True),
        sa.Column("peso", sa.String(length=80), nullable=True),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("pagina_referencia", sa.String(length=50), nullable=True),
        sa.Column(
            "origem_catalogo_mb",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("1"),
        ),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", name="uq_tormenta_equipamentos_nome"),
    )
    op.create_index("ix_tormenta_equipamentos_id", "tormenta_equipamentos", ["id"], unique=False)
    op.create_index("ix_tormenta_equipamentos_nome", "tormenta_equipamentos", ["nome"], unique=False)

    op.create_table(
        "tormenta_equipamentos_personagem",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("equipamento_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("notas", sa.String(length=500), nullable=True),
        sa.Column("adicionado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["personagem_id"],
            ["tormenta_personagens.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["equipamento_id"],
            ["tormenta_equipamentos.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "personagem_id",
            "equipamento_id",
            name="uq_tormenta_equipamento_personagem_par",
        ),
    )
    op.create_index(
        "ix_tormenta_equipamentos_personagem_id",
        "tormenta_equipamentos_personagem",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_tormenta_equipamentos_personagem_personagem_id",
        "tormenta_equipamentos_personagem",
        ["personagem_id"],
        unique=False,
    )
    op.create_index(
        "ix_tormenta_equipamentos_personagem_equipamento_id",
        "tormenta_equipamentos_personagem",
        ["equipamento_id"],
        unique=False,
    )

    op.create_table(
        "tormenta_consumiveis",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("categoria", sa.String(length=80), nullable=True),
        sa.Column("tipo", sa.String(length=80), nullable=True),
        sa.Column("custo", sa.String(length=80), nullable=True),
        sa.Column("peso", sa.String(length=80), nullable=True),
        sa.Column(
            "origem_catalogo_mb",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome", name="uq_tormenta_consumiveis_nome"),
    )
    op.create_index("ix_tormenta_consumiveis_id", "tormenta_consumiveis", ["id"], unique=False)
    op.create_index("ix_tormenta_consumiveis_nome", "tormenta_consumiveis", ["nome"], unique=False)

    op.create_table(
        "tormenta_consumiveis_personagem",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("consumivel_id", sa.Integer(), nullable=False),
        sa.Column("quantidade", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("notas", sa.String(length=500), nullable=True),
        sa.Column("adicionado_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["personagem_id"],
            ["tormenta_personagens.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["consumivel_id"],
            ["tormenta_consumiveis.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "personagem_id",
            "consumivel_id",
            name="uq_tormenta_consumivel_personagem_par",
        ),
    )
    op.create_index(
        "ix_tormenta_consumiveis_personagem_id",
        "tormenta_consumiveis_personagem",
        ["id"],
        unique=False,
    )
    op.create_index(
        "ix_tormenta_consumiveis_personagem_personagem_id",
        "tormenta_consumiveis_personagem",
        ["personagem_id"],
        unique=False,
    )
    op.create_index(
        "ix_tormenta_consumiveis_personagem_consumivel_id",
        "tormenta_consumiveis_personagem",
        ["consumivel_id"],
        unique=False,
    )

    from datetime import datetime, timezone

    from sqlalchemy.sql import column, table

    from app.games.tormenta.rules.catalogo_t20 import lista_equipamentos_mb_catalogo

    now = datetime.now(timezone.utc)
    rows = []
    for r in lista_equipamentos_mb_catalogo():
        nome = str(r.get("nome", "")).strip()[:200]
        if not nome:
            continue

        def _cell(key: str, mx: int):
            v = r.get(key)
            if v is None:
                return None
            t = str(v).strip()
            return t[:mx] if t else None

        rows.append(
            {
                "nome": nome,
                "categoria": _cell("categoria", 120),
                "secao": _cell("secao", 200),
                "custo": _cell("custo", 80),
                "dano_p": _cell("dano_p", 40),
                "dano_m": _cell("dano_m", 40),
                "tipo_dano": _cell("tipo_dano", 120),
                "critico": _cell("critico", 80),
                "alcance": _cell("alcance", 80),
                "peso": _cell("peso", 80),
                "descricao": None,
                "pagina_referencia": None,
                "origem_catalogo_mb": True,
                "criado_em": now,
            }
        )
    if rows:
        eq_tbl = table(
            "tormenta_equipamentos",
            column("nome", sa.String(200)),
            column("categoria", sa.String(120)),
            column("secao", sa.String(200)),
            column("custo", sa.String(80)),
            column("dano_p", sa.String(40)),
            column("dano_m", sa.String(40)),
            column("tipo_dano", sa.String(120)),
            column("critico", sa.String(80)),
            column("alcance", sa.String(80)),
            column("peso", sa.String(80)),
            column("descricao", sa.Text),
            column("pagina_referencia", sa.String(50)),
            column("origem_catalogo_mb", sa.Boolean),
            column("criado_em", sa.DateTime),
        )
        op.bulk_insert(eq_tbl, rows)


def downgrade() -> None:
    op.drop_index(
        "ix_tormenta_consumiveis_personagem_consumivel_id",
        table_name="tormenta_consumiveis_personagem",
    )
    op.drop_index(
        "ix_tormenta_consumiveis_personagem_personagem_id",
        table_name="tormenta_consumiveis_personagem",
    )
    op.drop_index(
        "ix_tormenta_consumiveis_personagem_id",
        table_name="tormenta_consumiveis_personagem",
    )
    op.drop_table("tormenta_consumiveis_personagem")
    op.drop_index("ix_tormenta_consumiveis_nome", table_name="tormenta_consumiveis")
    op.drop_index("ix_tormenta_consumiveis_id", table_name="tormenta_consumiveis")
    op.drop_table("tormenta_consumiveis")
    op.drop_index(
        "ix_tormenta_equipamentos_personagem_equipamento_id",
        table_name="tormenta_equipamentos_personagem",
    )
    op.drop_index(
        "ix_tormenta_equipamentos_personagem_personagem_id",
        table_name="tormenta_equipamentos_personagem",
    )
    op.drop_index(
        "ix_tormenta_equipamentos_personagem_id",
        table_name="tormenta_equipamentos_personagem",
    )
    op.drop_table("tormenta_equipamentos_personagem")
    op.drop_index("ix_tormenta_equipamentos_nome", table_name="tormenta_equipamentos")
    op.drop_index("ix_tormenta_equipamentos_id", table_name="tormenta_equipamentos")
    op.drop_table("tormenta_equipamentos")
