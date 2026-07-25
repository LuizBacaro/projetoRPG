"""GURPS: catalogo ficha - coluna meta_custo (JSON) para cost_model / opcoes discretas.

Revision ID: q2r3s4t5u6v7
Revises: p1q2r3s4t5u6
Create Date: 2026-07-24

Adiciona uma coluna JSON `meta_custo` opcional em
`gurps_catalogo_ficha_vantagens` e `gurps_catalogo_ficha_desvantagens` para
persistir o contrato enriquecido do catalogo (cost_model, opcoes_custo,
custo_por_nivel, faixa, autocontrole, etc.). Postgres usa `JSONB`, SQLite
(testes) usa `JSON` generico.

Idempotente: se a coluna já existir (schema criado/atualizado fora do Alembic
ou retry após falha parcial), a revision só avança o stamp.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "q2r3s4t5u6v7"
down_revision: Union[str, None] = "p1q2r3s4t5u6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _json_type():
    """JSONB no Postgres, JSON generico em SQLite/tests."""
    return sa.JSON().with_variant(postgresql.JSONB(), "postgresql")


def _tem_coluna(tabela: str, coluna: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if tabela not in inspector.get_table_names():
        return False
    return any(c["name"] == coluna for c in inspector.get_columns(tabela))


def upgrade() -> None:
    if not _tem_coluna("gurps_catalogo_ficha_vantagens", "meta_custo"):
        op.add_column(
            "gurps_catalogo_ficha_vantagens",
            sa.Column("meta_custo", _json_type(), nullable=True),
        )
    if not _tem_coluna("gurps_catalogo_ficha_desvantagens", "meta_custo"):
        op.add_column(
            "gurps_catalogo_ficha_desvantagens",
            sa.Column("meta_custo", _json_type(), nullable=True),
        )


def downgrade() -> None:
    if _tem_coluna("gurps_catalogo_ficha_desvantagens", "meta_custo"):
        op.drop_column("gurps_catalogo_ficha_desvantagens", "meta_custo")
    if _tem_coluna("gurps_catalogo_ficha_vantagens", "meta_custo"):
        op.drop_column("gurps_catalogo_ficha_vantagens", "meta_custo")
