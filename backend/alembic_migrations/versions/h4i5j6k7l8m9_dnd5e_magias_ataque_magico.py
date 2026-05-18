"""dnd5e_magias — ataque_magico (ranged/melee)."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "h4i5j6k7l8m9"
down_revision = "g3h4i5j6k7l8"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "dnd5e_magias",
        sa.Column("ataque_magico", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("dnd5e_magias", "ataque_magico")
