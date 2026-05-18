"""Tabelas dnd5e_magias, dnd5e_magias_classes e dnd5e_grimorio_magias.

Revision ID: e1d5e6f7a8b9
Revises: d7e8f9a0b1c2
Create Date: 2026-05-18
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e1d5e6f7a8b9"
down_revision: Union[str, None] = "d7e8f9a0b1c2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "dnd5e_magias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("nome", sa.String(length=160), nullable=False),
        sa.Column("nivel", sa.Integer(), nullable=False),
        sa.Column("escola", sa.String(length=40), nullable=True),
        sa.Column("tempo_conjuracao", sa.String(length=60), nullable=True),
        sa.Column("alcance_texto", sa.String(length=80), nullable=True),
        sa.Column("alcance_metros", sa.Integer(), nullable=True),
        sa.Column("duracao", sa.String(length=120), nullable=True),
        sa.Column("requer_concentracao", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("ritual", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("componentes_verbal", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("componentes_somatico", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("componentes_material", sa.Text(), nullable=True),
        sa.Column("material_consumido", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("material_custo_gp", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dano", sa.String(length=80), nullable=True),
        sa.Column("teste_resistencia", sa.String(length=40), nullable=True),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("descricao_nivel_superior", sa.Text(), nullable=True),
        sa.Column("pagina_referencia", sa.Integer(), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("criado_em", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_dnd5e_magias_nome", "dnd5e_magias", ["nome"])
    op.create_index("ix_dnd5e_magias_nivel", "dnd5e_magias", ["nivel"])
    op.create_index("ix_dnd5e_magias_escola", "dnd5e_magias", ["escola"])

    op.create_table(
        "dnd5e_magias_classes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("magia_id", sa.Integer(), nullable=False),
        sa.Column("classe_slug", sa.String(length=40), nullable=False),
        sa.Column("nivel", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["magia_id"], ["dnd5e_magias.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("magia_id", "classe_slug", name="uq_dnd5e_magias_classes_magia_classe"),
    )
    op.create_index("ix_dnd5e_magias_classes_classe", "dnd5e_magias_classes", ["classe_slug"])

    op.create_table(
        "dnd5e_grimorio_magias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("personagem_id", sa.Integer(), nullable=False),
        sa.Column("magia_id", sa.Integer(), nullable=False),
        sa.Column("classe", sa.String(length=50), nullable=False),
        sa.Column("favorita", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("anotacoes", sa.Text(), nullable=True),
        sa.Column("origem", sa.String(length=30), nullable=False, server_default="SELECAO_MANUAL"),
        sa.Column("adicionada_em", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["personagem_id"], ["dnd5e_personagens.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["magia_id"], ["dnd5e_magias.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "personagem_id",
            "magia_id",
            "classe",
            name="uq_dnd5e_grimorio_personagem_magia_classe",
        ),
    )
    op.create_index(
        "ix_dnd5e_grimorio_personagem", "dnd5e_grimorio_magias", ["personagem_id"]
    )


def downgrade() -> None:
    op.drop_table("dnd5e_grimorio_magias")
    op.drop_table("dnd5e_magias_classes")
    op.drop_table("dnd5e_magias")
