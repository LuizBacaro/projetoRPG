"""
add_combatente_divindade

Migração incremental: adiciona coluna divindade em combatentes.
- Nullable com default '' para compatibilidade de dados legados.
- Idempotente para não falhar em ambientes já alterados.
"""

from typing import Union

from alembic import op
import sqlalchemy as sa


revision: str = "5e72b9a1c4d0"
down_revision: Union[str, None] = "c8d4e2f7a901"
branch_labels = None
depends_on = None


def _coluna_existe(tabela: str, coluna: str) -> bool:
    try:
        bind = op.get_bind()
        if hasattr(bind, "__class__") and "Mock" in bind.__class__.__name__:
            return False
        inspector = sa.inspect(bind)
        return coluna in [c["name"] for c in inspector.get_columns(tabela)]
    except Exception:
        return False


def upgrade() -> None:
    if not _coluna_existe("combatentes", "divindade"):
        op.add_column(
            "combatentes",
            sa.Column("divindade", sa.String(), nullable=True, server_default=""),
        )


def downgrade() -> None:
    if _coluna_existe("combatentes", "divindade"):
        op.drop_column("combatentes", "divindade")
