"""Tabelas núcleo GURPS (campanhas, personagens, combate).

Revision ID: b1a2c3d4e5f6
Revises: c3d4e5f6a7b8
Create Date: 2026-05-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b1a2c3d4e5f6"
down_revision: Union[str, None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gurps_campanhas",
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
        sa.ForeignKeyConstraint(["mestre_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gurps_campanhas_id", "gurps_campanhas", ["id"], unique=False)
    op.create_index(
        "ix_gurps_campanhas_mestre_id", "gurps_campanhas", ["mestre_id"], unique=False
    )

    op.create_table(
        "gurps_personagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dono_id", sa.Integer(), nullable=True),
        sa.Column("campanha_id", sa.Integer(), nullable=True),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("conceito", sa.String(length=200), nullable=True),
        sa.Column("reacao", sa.String(length=40), nullable=True),
        sa.Column("idade", sa.String(length=80), nullable=True),
        sa.Column("foto_url", sa.String(length=500), nullable=True),
        sa.Column("iniciativa", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("st_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("st_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("dx_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dx_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("iq_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("iq_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("ht_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ht_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("vontade_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("vontade_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("percepcao_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("percepcao_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("pvs_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pvs_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("pvs_atual", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("fadiga_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("fadiga_valor", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("fadiga_atual", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("velocidade_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("velocidade_valor", sa.Numeric(10, 2), nullable=False, server_default="5.00"),
        sa.Column("deslocamento_custo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deslocamento_valor", sa.Integer(), nullable=False, server_default="5"),
        sa.Column("esquiva", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("aparar", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("bloqueio", sa.String(length=20), nullable=True),
        sa.Column("dano_impacto", sa.String(length=40), nullable=True),
        sa.Column("dano_balanco", sa.String(length=40), nullable=True),
        sa.Column("pontos_atributos", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pontos_vantagens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pontos_desvantagens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pontos_pericias", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("pontos_total", sa.Integer(), nullable=False, server_default="0"),
        sa.CheckConstraint(
            "tipo IN ('jogador', 'monstro', 'npc')",
            name="ck_gurps_personagens_tipo_valido",
        ),
        sa.ForeignKeyConstraint(["campanha_id"], ["gurps_campanhas.id"]),
        sa.ForeignKeyConstraint(["dono_id"], ["usuarios.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gurps_personagens_id", "gurps_personagens", ["id"], unique=False)
    op.create_index(
        "ix_gurps_personagens_dono_id", "gurps_personagens", ["dono_id"], unique=False
    )
    op.create_index(
        "ix_gurps_personagens_campanha_id",
        "gurps_personagens",
        ["campanha_id"],
        unique=False,
    )

    op.create_table(
        "gurps_personagem_vantagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=500), nullable=False),
        sa.Column("custo", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(
            ["personagem_id"],
            ["gurps_personagens.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_gurps_vantagens_personagem_id",
        "gurps_personagem_vantagens",
        ["personagem_id"],
        unique=False,
    )

    op.create_table(
        "gurps_personagem_desvantagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=500), nullable=False),
        sa.Column("custo", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(
            ["personagem_id"],
            ["gurps_personagens.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_gurps_desvantagens_personagem_id",
        "gurps_personagem_desvantagens",
        ["personagem_id"],
        unique=False,
    )

    op.create_table(
        "gurps_personagem_pericias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=500), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("nh", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("custo", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(
            ["personagem_id"],
            ["gurps_personagens.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_gurps_pericias_personagem_id",
        "gurps_personagem_pericias",
        ["personagem_id"],
        unique=False,
    )

    op.create_table(
        "gurps_combates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagens_ids", sa.JSON(), nullable=False),
        sa.Column("turno_atual", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("rodada_atual", sa.Integer(), nullable=True, server_default="1"),
        sa.Column("ativo", sa.Boolean(), nullable=True, server_default=sa.text("true")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_gurps_combates_id", "gurps_combates", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_gurps_combates_id", table_name="gurps_combates")
    op.drop_table("gurps_combates")

    op.drop_index("ix_gurps_pericias_personagem_id", table_name="gurps_personagem_pericias")
    op.drop_table("gurps_personagem_pericias")

    op.drop_index(
        "ix_gurps_desvantagens_personagem_id", table_name="gurps_personagem_desvantagens"
    )
    op.drop_table("gurps_personagem_desvantagens")

    op.drop_index("ix_gurps_vantagens_personagem_id", table_name="gurps_personagem_vantagens")
    op.drop_table("gurps_personagem_vantagens")

    op.drop_index("ix_gurps_personagens_campanha_id", table_name="gurps_personagens")
    op.drop_index("ix_gurps_personagens_dono_id", table_name="gurps_personagens")
    op.drop_index("ix_gurps_personagens_id", table_name="gurps_personagens")
    op.drop_table("gurps_personagens")

    op.drop_index("ix_gurps_campanhas_mestre_id", table_name="gurps_campanhas")
    op.drop_index("ix_gurps_campanhas_id", table_name="gurps_campanhas")
    op.drop_table("gurps_campanhas")
