"""Tabela tormenta_personagens (ficha Módulo Básico — cadastro digital).

Revision ID: e1f2a3b4c5d6
Revises: c4e8d2a9f1b3
Create Date: 2026-05-11
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e1f2a3b4c5d6"
down_revision: Union[str, None] = "c4e8d2a9f1b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "tormenta_personagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dono_id", sa.Integer(), nullable=True),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("jogador_nome", sa.String(length=120), nullable=True),
        sa.Column("raca", sa.String(length=120), nullable=True),
        sa.Column("classe_nivel", sa.String(length=160), nullable=True),
        sa.Column("sexo", sa.String(length=40), nullable=True),
        sa.Column("idade", sa.String(length=80), nullable=True),
        sa.Column("tendencia", sa.String(length=80), nullable=True),
        sa.Column("divindade", sa.String(length=120), nullable=True),
        sa.Column("for_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("des_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("con_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("int_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("sab_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("car_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("pv_max", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("pv_atual", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("pa_max", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pa_atual", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ca", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("rd", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("nivel", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("iniciativa", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deslocamento", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("tamanho", sa.String(length=80), nullable=False, server_default=""),
        sa.Column("fort_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ref_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("von_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "ficha_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
        sa.CheckConstraint(
            "tipo IN ('jogador', 'monstro', 'npc')",
            name="ck_tormenta_personagens_tipo_valido",
        ),
        sa.ForeignKeyConstraint(["dono_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_tormenta_personagens_id", "tormenta_personagens", ["id"], unique=False
    )
    op.create_index(
        "ix_tormenta_personagens_dono_id",
        "tormenta_personagens",
        ["dono_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_tormenta_personagens_dono_id", table_name="tormenta_personagens")
    op.drop_index("ix_tormenta_personagens_id", table_name="tormenta_personagens")
    op.drop_table("tormenta_personagens")
