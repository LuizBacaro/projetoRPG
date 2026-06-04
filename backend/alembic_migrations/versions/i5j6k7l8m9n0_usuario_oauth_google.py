"""usuario_oauth_google

Revision ID: i5j6k7l8m9n0
Revises: h4i5j6k7l8m9
Create Date: 2026-06-04

OAuth Google: senha_hash opcional + oauth_provider/oauth_subject.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.exc import NoSuchTableError

revision: str = "i5j6k7l8m9n0"
down_revision: Union[str, None] = "h4i5j6k7l8m9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _coluna_existe(tabela: str, coluna: str) -> bool:
    try:
        bind = op.get_bind()
        colunas = [c["name"] for c in sa.inspect(bind).get_columns(tabela)]
        return coluna in colunas
    except NoSuchTableError:
        return False


def upgrade() -> None:
    if not _coluna_existe("usuarios", "oauth_provider"):
        with op.batch_alter_table("usuarios") as batch_op:
            batch_op.add_column(
                sa.Column("oauth_provider", sa.String(32), nullable=True)
            )
            batch_op.add_column(
                sa.Column("oauth_subject", sa.String(128), nullable=True)
            )
            batch_op.alter_column(
                "senha_hash",
                existing_type=sa.String(255),
                nullable=True,
            )
        op.create_index(
            "ix_usuarios_oauth_provider_subject",
            "usuarios",
            ["oauth_provider", "oauth_subject"],
            unique=True,
        )


def downgrade() -> None:
    if _coluna_existe("usuarios", "oauth_provider"):
        op.drop_index("ix_usuarios_oauth_provider_subject", table_name="usuarios")
        with op.batch_alter_table("usuarios") as batch_op:
            batch_op.drop_column("oauth_subject")
            batch_op.drop_column("oauth_provider")
            batch_op.alter_column(
                "senha_hash",
                existing_type=sa.String(255),
                nullable=False,
            )
