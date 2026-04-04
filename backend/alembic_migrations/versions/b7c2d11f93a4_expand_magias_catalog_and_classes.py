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


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(col.get("name") == column_name for col in inspector.get_columns(table_name))


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(idx.get("name") == index_name for idx in inspector.get_indexes(table_name))


def _unique_constraint_exists(bind, table_name: str, constraint_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(constraint.get("name") == constraint_name for constraint in inspector.get_unique_constraints(table_name))


def upgrade() -> None:
    bind = op.get_bind()

    # Limpa resquicio de tentativa anterior interrompida no modo batch do SQLite.
    if _table_exists(bind, "_alembic_tmp_magias"):
        op.execute(sa.text("DROP TABLE _alembic_tmp_magias"))

    columns_to_add = [
        sa.Column("nome_en", sa.String(length=100), nullable=True),
        sa.Column("descritor", sa.String(length=200), nullable=True),
        sa.Column("componente_extra", sa.String(length=300), nullable=True),
        sa.Column("resistencia_magia_texto", sa.String(length=50), nullable=True),
        sa.Column("descricao_en", sa.String(length=1000), nullable=True),
        sa.Column("e_magia_dominio", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("dominios", sa.String(length=250), nullable=True),
        sa.Column("pagina_referencia", sa.Integer(), nullable=True),
    ]
    for column in columns_to_add:
        if not _column_exists(bind, "magias", column.name):
            with op.batch_alter_table("magias") as batch_op:
                batch_op.add_column(column)

    if not _table_exists(bind, "magias_classes"):
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

    if not _index_exists(bind, "magias_classes", "ix_magias_classes_id"):
        op.create_index("ix_magias_classes_id", "magias_classes", ["id"], unique=False)
    if not _index_exists(bind, "magias_classes", "ix_magias_classes_magia_id"):
        op.create_index("ix_magias_classes_magia_id", "magias_classes", ["magia_id"], unique=False)
    if not _index_exists(bind, "magias_classes", "ix_magias_classes_classe"):
        op.create_index("ix_magias_classes_classe", "magias_classes", ["classe"], unique=False)

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

    if not _unique_constraint_exists(bind, "magias", "uq_magias_nome"):
        with op.batch_alter_table("magias") as batch_op:
            batch_op.create_unique_constraint("uq_magias_nome", ["nome"])


def downgrade() -> None:
    bind = op.get_bind()

    if _unique_constraint_exists(bind, "magias", "uq_magias_nome"):
        with op.batch_alter_table("magias") as batch_op:
            batch_op.drop_constraint("uq_magias_nome", type_="unique")

    if _index_exists(bind, "magias_classes", "ix_magias_classes_classe"):
        op.drop_index("ix_magias_classes_classe", table_name="magias_classes")
    if _index_exists(bind, "magias_classes", "ix_magias_classes_magia_id"):
        op.drop_index("ix_magias_classes_magia_id", table_name="magias_classes")
    if _index_exists(bind, "magias_classes", "ix_magias_classes_id"):
        op.drop_index("ix_magias_classes_id", table_name="magias_classes")
    if _table_exists(bind, "magias_classes"):
        op.drop_table("magias_classes")

    columns_to_drop = [
        "pagina_referencia",
        "dominios",
        "e_magia_dominio",
        "descricao_en",
        "resistencia_magia_texto",
        "componente_extra",
        "descritor",
        "nome_en",
    ]
    for column_name in columns_to_drop:
        if _column_exists(bind, "magias", column_name):
            with op.batch_alter_table("magias") as batch_op:
                batch_op.drop_column(column_name)
