"""GURPS: extras_json na ficha (encargo, locais de acerto, notas livres).

Revision ID: e8f9a0b1c2d3
Revises: b1a2c3d4e5f6
Create Date: 2026-05-01
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e8f9a0b1c2d3"
down_revision: Union[str, None] = "b1a2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "gurps_personagens",
        sa.Column(
            "extras_json",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'{}'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("gurps_personagens", "extras_json")
