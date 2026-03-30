"""add_soft_delete_columns

Revision ID: e4a1f9c8d2b3
Revises: c1b7e4d2a9f0
Create Date: 2026-03-29 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4a1f9c8d2b3"
down_revision: Union[str, None] = "c1b7e4d2a9f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _coluna_existe(tabela: str, coluna: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    colunas = [c["name"] for c in inspector.get_columns(tabela)]
    return coluna in colunas


def _indice_existe(tabela: str, indice: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indices = [i["name"] for i in inspector.get_indexes(tabela)]
    return indice in indices


def upgrade() -> None:
    for tabela in ("combatentes", "equipamentos", "talentos", "pericias"):
        if not _coluna_existe(tabela, "deleted_at"):
            op.add_column(tabela, sa.Column("deleted_at", sa.DateTime(), nullable=True))

    indices = {
        "combatentes": "ix_combatentes_deleted_at",
        "equipamentos": "ix_equipamentos_deleted_at",
        "talentos": "ix_talentos_deleted_at",
        "pericias": "ix_pericias_deleted_at",
    }
    for tabela, indice in indices.items():
        if not _indice_existe(tabela, indice):
            op.create_index(indice, tabela, ["deleted_at"], unique=False)


def downgrade() -> None:
    indices = {
        "combatentes": "ix_combatentes_deleted_at",
        "equipamentos": "ix_equipamentos_deleted_at",
        "talentos": "ix_talentos_deleted_at",
        "pericias": "ix_pericias_deleted_at",
    }
    for tabela, indice in indices.items():
        if _indice_existe(tabela, indice):
            op.drop_index(indice, table_name=tabela)

    for tabela in ("combatentes", "equipamentos", "talentos", "pericias"):
        if _coluna_existe(tabela, "deleted_at"):
            op.drop_column(tabela, "deleted_at")