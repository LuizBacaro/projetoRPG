"""add_combatente_owner

Revision ID: 9f3c2f7b1a01
Revises: 630072bd328c
Create Date: 2026-03-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9f3c2f7b1a01"
down_revision: Union[str, None] = "630072bd328c"
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


def _sql_pick_admin_owner(dialect_name: str) -> str:
    """
    Postgres ENUM `perfilusuario` pode ter labels em minúsculas (migração 001) ou os nomes
    Python do Enum (ADMINISTRADOR) conforme create_all/SQLAlchemy — comparar como texto.
    """
    if dialect_name == "postgresql":
        return """
            SELECT id
            FROM usuarios
            WHERE CAST(perfil AS TEXT) ILIKE 'administrador'
              AND ativo IS TRUE
            ORDER BY id
            LIMIT 1
            """
    return """
            SELECT id
            FROM usuarios
            WHERE perfil = 'administrador' AND ativo = 1
            ORDER BY id
            LIMIT 1
            """


def upgrade() -> None:
    if not _coluna_existe("combatentes", "dono_id"):
        op.add_column("combatentes", sa.Column("dono_id", sa.Integer(), nullable=True))

    if not _indice_existe("combatentes", "ix_combatentes_dono_id"):
        op.create_index("ix_combatentes_dono_id", "combatentes", ["dono_id"], unique=False)

    bind = op.get_bind()

    # Backfill: atribui combatentes sem dono a um admin ativo, ou ao primeiro usuário disponível.
    owner_id = bind.execute(sa.text(_sql_pick_admin_owner(bind.dialect.name))).scalar()

    if owner_id is None:
        owner_id = bind.execute(
            sa.text(
                """
                SELECT id
                FROM usuarios
                ORDER BY id
                LIMIT 1
                """
            )
        ).scalar()

    if owner_id is not None:
        bind.execute(
            sa.text(
                """
                UPDATE combatentes
                SET dono_id = :owner_id
                WHERE dono_id IS NULL
                """
            ),
            {"owner_id": owner_id},
        )


def downgrade() -> None:
    if _indice_existe("combatentes", "ix_combatentes_dono_id"):
        op.drop_index("ix_combatentes_dono_id", table_name="combatentes")

    if _coluna_existe("combatentes", "dono_id"):
        op.drop_column("combatentes", "dono_id")
