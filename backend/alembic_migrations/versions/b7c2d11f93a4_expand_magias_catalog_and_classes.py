"""expand_magias_catalog_and_classes

Revision ID: b7c2d11f93a4
Revises: a35b1f4c9d10
Create Date: 2026-03-30 20:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b7c2d11f93a4"
down_revision: Union[str, None] = "a35b1f4c9d10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("magias") as batch_op:
        batch_op.add_column(sa.Column("nome_en", sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column("descritor", sa.String(length=200), nullable=True))
        batch_op.add_column(sa.Column("componente_extra", sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column("resistencia_magia_texto", sa.String(length=50), nullable=True))
        batch_op.add_column(sa.Column("descricao_en", sa.String(length=1000), nullable=True))
        batch_op.add_column(sa.Column("e_magia_dominio", sa.Boolean(), nullable=False, server_default=sa.text("0")))
        batch_op.add_column(sa.Column("dominios", sa.String(length=250), nullable=True))
        batch_op.add_column(sa.Column("pagina_referencia", sa.Integer(), nullable=True))

    op.create_table(
        "magias_classes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("magia_id", sa.Integer(), nullable=False),
        sa.Column("classe", sa.String(length=50), nullable=False),
        sa.Column("nivel", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["magia_id"], ["magias.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("magia_id", "classe", name="uq_magias_classes_magia_classe"),
    )
    op.create_index("ix_magias_classes_id", "magias_classes", ["id"], unique=False)
    op.create_index("ix_magias_classes_magia_id", "magias_classes", ["magia_id"], unique=False)
    op.create_index("ix_magias_classes_classe", "magias_classes", ["classe"], unique=False)

    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO magias_classes (magia_id, classe, nivel)
            SELECT m.id, UPPER(TRIM(m.classe)), m.nivel
            FROM magias m
            WHERE m.classe IS NOT NULL
              AND TRIM(m.classe) <> ''
              AND m.nivel IS NOT NULL
              AND NOT EXISTS (
                SELECT 1
                FROM magias_classes mc
                WHERE mc.magia_id = m.id
                  AND mc.classe = UPPER(TRIM(m.classe))
              )
            """
        )
    )

    bind.execute(
        sa.text(
            """
            WITH ranked AS (
                SELECT id,
                       nome,
                       ROW_NUMBER() OVER (PARTITION BY nome ORDER BY id) AS rn
                FROM magias
                WHERE nome IS NOT NULL
            )
            UPDATE magias
            SET nome = nome || ' #' || id
            WHERE id IN (SELECT id FROM ranked WHERE rn > 1)
            """
        )
    )

    with op.batch_alter_table("magias") as batch_op:
        batch_op.create_unique_constraint("uq_magias_nome", ["nome"])


def downgrade() -> None:
    with op.batch_alter_table("magias") as batch_op:
        batch_op.drop_constraint("uq_magias_nome", type_="unique")

    op.drop_index("ix_magias_classes_classe", table_name="magias_classes")
    op.drop_index("ix_magias_classes_magia_id", table_name="magias_classes")
    op.drop_index("ix_magias_classes_id", table_name="magias_classes")
    op.drop_table("magias_classes")

    with op.batch_alter_table("magias") as batch_op:
        batch_op.drop_column("pagina_referencia")
        batch_op.drop_column("dominios")
        batch_op.drop_column("e_magia_dominio")
        batch_op.drop_column("descricao_en")
        batch_op.drop_column("resistencia_magia_texto")
        batch_op.drop_column("componente_extra")
        batch_op.drop_column("descritor")
        batch_op.drop_column("nome_en")
