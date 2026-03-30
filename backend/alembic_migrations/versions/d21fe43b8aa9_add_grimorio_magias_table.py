"""add_grimorio_magias_table

Revision ID: d21fe43b8aa9
Revises: b7c2d11f93a4
Create Date: 2026-03-30 21:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d21fe43b8aa9"
down_revision: Union[str, None] = "b7c2d11f93a4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "grimorio_magias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("combatente_id", sa.Integer(), nullable=False),
        sa.Column("magia_id", sa.Integer(), nullable=False),
        sa.Column("classe", sa.String(length=50), nullable=False),
        sa.Column("favorita", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("anotacoes", sa.Text(), nullable=True),
        sa.Column("origem", sa.String(length=30), nullable=False, server_default=sa.text("'SELECAO_MANUAL'")),
        sa.Column("adicionada_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["combatente_id"], ["combatentes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["magia_id"], ["magias.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("combatente_id", "magia_id", "classe", name="uq_grimorio_combatente_magia_classe"),
    )
    op.create_index("ix_grimorio_magias_id", "grimorio_magias", ["id"], unique=False)
    op.create_index("ix_grimorio_magias_combatente_id", "grimorio_magias", ["combatente_id"], unique=False)
    op.create_index("ix_grimorio_magias_magia_id", "grimorio_magias", ["magia_id"], unique=False)
    op.create_index("ix_grimorio_magias_classe", "grimorio_magias", ["classe"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_grimorio_magias_classe", table_name="grimorio_magias")
    op.drop_index("ix_grimorio_magias_magia_id", table_name="grimorio_magias")
    op.drop_index("ix_grimorio_magias_combatente_id", table_name="grimorio_magias")
    op.drop_index("ix_grimorio_magias_id", table_name="grimorio_magias")
    op.drop_table("grimorio_magias")
