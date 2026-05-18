"""dnd5e_magias — nome_en, descricao_en (i18n SRD/PHB)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "g3h4i5j6k7l8"
down_revision = "f2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "dnd5e_magias",
        sa.Column("nome_en", sa.String(length=160), nullable=True),
    )
    op.add_column(
        "dnd5e_magias",
        sa.Column("descricao_en", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dnd5e_magias", "descricao_en")
    op.drop_column("dnd5e_magias", "nome_en")
