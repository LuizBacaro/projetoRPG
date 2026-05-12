"""Adicionar campos equipamentos manual

Revision ID: af4a62e567b7
Revises: 173c62f6aa14
Create Date: 2026-04-18 08:15:07.566810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af4a62e567b7'
down_revision: Union[str, None] = '874ba656c7c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Adiciona novos campos à tabela equipamentos."""

    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "equipamentos" not in insp.get_table_names():
        return
    colunas_existentes = {c["name"] for c in insp.get_columns("equipamentos")}

    campos = [
        ("categoria", sa.String(50)),
        ("subcategoria", sa.String(100)),
        ("custo", sa.String(50)),
        ("dano_pequeno", sa.String(20)),
        ("dano_medio", sa.String(20)),
        ("critico", sa.String(20)),
        ("alcance_incremento", sa.String(50)),
        ("peso", sa.String(20)),
        ("tipo_dano", sa.String(50)),
    ]

    # Postgres: após um erro SQL a transação fica abortada — não usar try/except por coluna.
    for nome_campo, tipo in campos:
        if nome_campo in colunas_existentes:
            continue
        op.add_column("equipamentos", sa.Column(nome_campo, tipo, nullable=True))


def downgrade() -> None:
    """Remove novos campos da tabela equipamentos."""

    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "equipamentos" not in insp.get_table_names():
        return
    colunas_existentes = {c["name"] for c in insp.get_columns("equipamentos")}

    campos_remover = [
        "tipo_dano",
        "peso",
        "alcance_incremento",
        "critico",
        "dano_medio",
        "dano_pequeno",
        "custo",
        "subcategoria",
        "categoria",
    ]

    for nome_campo in campos_remover:
        if nome_campo not in colunas_existentes:
            continue
        op.drop_column("equipamentos", nome_campo)
