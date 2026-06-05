"""oauth_usuario_schema_repair

Revision ID: j6k7l8m9n0o1
Revises: i5j6k7l8m9n0
Create Date: 2026-06-05

Reaplica colunas OAuth em auth.usuarios quando i5j6k7l8m9n0 foi stamped sem DDL.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text
from sqlalchemy.exc import NoSuchTableError

revision: str = "j6k7l8m9n0o1"
down_revision: Union[str, None] = "i5j6k7l8m9n0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

IDX_OAUTH = "ix_usuarios_oauth_provider_subject"


def _schema_usuarios(bind) -> str | None:
    if bind.dialect.name != "postgresql":
        return None
    insp = sa.inspect(bind)
    for schema in ("auth", "public"):
        if "usuarios" in insp.get_table_names(schema=schema):
            return schema
    return None


def _coluna_existe(tabela: str, coluna: str, schema: str | None = None) -> bool:
    try:
        bind = op.get_bind()
        colunas = [c["name"] for c in sa.inspect(bind).get_columns(tabela, schema=schema)]
        return coluna in colunas
    except NoSuchTableError:
        return False


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        bind.execute(text("SET search_path TO auth, dnd35, public"))
    schema = _schema_usuarios(bind)
    if schema is None and bind.dialect.name == "postgresql":
        return

    if not _coluna_existe("usuarios", "oauth_provider", schema=schema):
        op.add_column(
            "usuarios",
            sa.Column("oauth_provider", sa.String(32), nullable=True),
            schema=schema,
        )
    if not _coluna_existe("usuarios", "oauth_subject", schema=schema):
        op.add_column(
            "usuarios",
            sa.Column("oauth_subject", sa.String(128), nullable=True),
            schema=schema,
        )
    cols = sa.inspect(bind).get_columns("usuarios", schema=schema)
    senha = next((c for c in cols if c["name"] == "senha_hash"), None)
    if senha and not senha.get("nullable", True):
        if bind.dialect.name == "sqlite":
            with op.batch_alter_table("usuarios", schema=schema) as batch_op:
                batch_op.alter_column(
                    "senha_hash",
                    existing_type=sa.String(255),
                    nullable=True,
                )
        else:
            op.alter_column(
                "usuarios",
                "senha_hash",
                existing_type=sa.String(255),
                nullable=True,
                schema=schema,
            )
    if bind.dialect.name == "postgresql":
        qual = f'"{schema}"."usuarios"' if schema else "usuarios"
        op.execute(
            text(
                f"CREATE UNIQUE INDEX IF NOT EXISTS {IDX_OAUTH} "
                f"ON {qual} (oauth_provider, oauth_subject)"
            )
        )


def downgrade() -> None:
    pass
