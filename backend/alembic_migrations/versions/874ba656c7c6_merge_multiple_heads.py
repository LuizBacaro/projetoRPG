"""Merge multiple heads

Revision ID: 874ba656c7c6
Revises: 8d9c1b7a4f21, a1b2c3d4e5f6
Create Date: 2026-04-18 08:14:50.952264

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '874ba656c7c6'
down_revision: Union[str, None] = ('8d9c1b7a4f21', 'a1b2c3d4e5f6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
