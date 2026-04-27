"""Fase C: preparar schemas auth e dnd35 (Postgres).

Revision ID: fase_c_schemas_auth_dnd35
Revises: a7b9d3e1c2f4
Create Date: 2026-04-27 09:05:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "fase_c_schemas_auth_dnd35"
down_revision: Union[str, None] = "a7b9d3e1c2f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_postgres() -> bool:
    bind = op.get_bind()
    return bind.dialect.name == "postgresql"


AUTH_TABLES = [
    "usuarios",
    "games_catalog",
    "user_game_memberships",
]

# Ordem intencional: primeiro raízes, depois dependentes (ver inventário técnico).
DND35_TABLES = [
    # raízes
    "condicoes",
    "equipamentos",
    "armaduras_protecao",
    "magias",
    "pericias",
    "talentos",
    "campanhas",
    "divindades_custom",
    # dependentes
    "combatentes",
    "combates",
    "combates_historico",
    "campanhas_sessoes",
    "combatente_condicoes",
    "ataques",
    "equipamentos_jogador",
    "armaduras_protecao_jogador",
    "magias_classes",
    "magias_slots",
    "magias_preparadas",
    "pericias_classes",
    "pericia_jogadores",
    "talentos_jogador",
    "grimorio_magias",
    "grimorio_historico_troca",
    "grimorio_notificacoes",
    "magia_historico",
]


def _create_schemas_if_needed() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS auth"))
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS dnd35"))


def _table_exists(schema: str, table: str) -> bool:
    bind = op.get_bind()
    full_name = f"{schema}.{table}"
    exists = bind.execute(
        sa.text("SELECT to_regclass(:full_name) IS NOT NULL"),
        {"full_name": full_name},
    ).scalar()
    return bool(exists)


def _move_table_if_exists(table: str, source_schema: str, target_schema: str) -> None:
    if not _table_exists(source_schema, table):
        return
    op.execute(
        sa.text(f'ALTER TABLE "{source_schema}"."{table}" SET SCHEMA "{target_schema}"')
    )


def upgrade() -> None:
    """Move tabelas de public para schemas auth/dnd35 (somente Postgres)."""
    if not _is_postgres():
        # Em dev/teste com SQLite, não há schemas físicos.
        return

    _create_schemas_if_needed()

    for table in AUTH_TABLES:
        _move_table_if_exists(table, source_schema="public", target_schema="auth")

    for table in DND35_TABLES:
        _move_table_if_exists(table, source_schema="public", target_schema="dnd35")


def downgrade() -> None:
    """Move tabelas de auth/dnd35 de volta para public (somente Postgres)."""
    if not _is_postgres():
        return

    # Ordem inversa para reduzir risco de FK/interdependência.
    for table in reversed(DND35_TABLES):
        _move_table_if_exists(table, source_schema="dnd35", target_schema="public")

    for table in reversed(AUTH_TABLES):
        _move_table_if_exists(table, source_schema="auth", target_schema="public")

