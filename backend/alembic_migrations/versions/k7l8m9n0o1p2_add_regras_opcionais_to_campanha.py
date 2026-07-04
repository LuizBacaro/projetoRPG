"""Migration: add regras_opcionais_ativas to tormenta_campanhas.

Revision ID: k7l8m9n0o1p2
Revises: j6k7l8m9n0o1
Create Date: 2026-07-04
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "k7l8m9n0o1p2"
down_revision = "j6k7l8m9n0o1"
branch_labels = None
depends_on = None


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(col.get("name") == column_name for col in inspector.get_columns(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    if not _column_exists(bind, "tormenta_campanhas", "regras_opcionais_ativas"):
        op.add_column(
            "tormenta_campanhas",
            sa.Column(
                "regras_opcionais_ativas",
                sa.JSON(),
                nullable=True,
                comment="Lista de slugs de regras opcionais ativas (ex.: combate_avancado, lesoes). Heróis de Arton cap.4.",
            ),
        )


def downgrade() -> None:
    bind = op.get_bind()
    if _column_exists(bind, "tormenta_campanhas", "regras_opcionais_ativas"):
        op.drop_column("tormenta_campanhas", "regras_opcionais_ativas")
