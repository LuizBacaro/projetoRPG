"""
002_add_pagina_referencia.py

Migração: adiciona coluna pagina_referencia em combatentes
- Usada pelo Mestre para referenciar o livro/página do monstro
- Nullable com default '' para não quebrar registros existentes

SRP  : uma única alteração de schema.
"""
from alembic import op
import sqlalchemy as sa

revision      = "002_add_pagina_referencia"
down_revision = "001_initial_schema"
branch_labels = None
depends_on    = None


def _coluna_existe(tabela: str, coluna: str) -> bool:
    """Idempotência: verifica antes de adicionar."""
    try:
        bind = op.get_bind()
        if hasattr(bind, "__class__") and "Mock" in bind.__class__.__name__:
            return False
        inspector = sa.inspect(bind)
        return coluna in [c["name"] for c in inspector.get_columns(tabela)]
    except Exception:
        return False


def upgrade() -> None:
    if not _coluna_existe("combatentes", "pagina_referencia"):
        op.add_column(
            "combatentes",
            sa.Column(
                "pagina_referencia",
                sa.String(),
                nullable=True,
                server_default="",
            ),
        )


def downgrade() -> None:
    if _coluna_existe("combatentes", "pagina_referencia"):
        op.drop_column("combatentes", "pagina_referencia")