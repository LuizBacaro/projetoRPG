"""add_performance_indexes_catalogs

Revision ID: 8d9c1b7a4f21
Revises: 66fcb1736292
Create Date: 2026-04-12 12:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8d9c1b7a4f21"
down_revision: Union[str, None] = "66fcb1736292"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _index_exists(bind, table_name: str, index_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    return any(idx.get("name") == index_name for idx in inspector.get_indexes(table_name))


def _create_index_if_missing(bind, table_name: str, index_name: str, columns: list[str]) -> None:
    if _table_exists(bind, table_name) and not _index_exists(bind, table_name, index_name):
        op.create_index(index_name, table_name, columns, unique=False)


def upgrade() -> None:
    bind = op.get_bind()

    # Pericias: lookup por classe + pericia
    _create_index_if_missing(
        bind,
        "pericias_classes",
        "ix_pericias_classes_classe_nome_pericia",
        ["classe_nome", "pericia_id"],
    )

    # Pericia do jogador: lookup por combatente/pericia
    _create_index_if_missing(
        bind,
        "pericia_jogadores",
        "ix_pericia_jogadores_combatente_pericia",
        ["combatente_id", "pericia_id"],
    )

    # Magias por classe/nivel na tabela normalizada
    _create_index_if_missing(
        bind,
        "magias_classes",
        "ix_magias_classes_classe_nivel_magia",
        ["classe", "nivel", "magia_id"],
    )

    # Slots por combatente ordenando por nivel
    _create_index_if_missing(
        bind,
        "magias_slots",
        "ix_magias_slots_combatente_nivel",
        ["combatente_id", "nivel"],
    )

    # Preparadas por combatente com ordenacao por slot
    _create_index_if_missing(
        bind,
        "magias_preparadas",
        "ix_magias_preparadas_combatente_slot_magia",
        ["combatente_id", "nivel_slot", "magia_id"],
    )

    # Grimorio por combatente/classe com ordenacao temporal
    _create_index_if_missing(
        bind,
        "grimorio_magias",
        "ix_grimorio_magias_combatente_classe_adicionada",
        ["combatente_id", "classe", "adicionada_em"],
    )

    # Catalogos ativos e nao deletados ordenados por nome
    _create_index_if_missing(
        bind,
        "equipamentos",
        "ix_equipamentos_ativo_deleted_nome",
        ["ativo", "deleted_at", "nome"],
    )
    _create_index_if_missing(
        bind,
        "talentos",
        "ix_talentos_ativo_deleted_nome",
        ["ativo", "deleted_at", "nome"],
    )

    # Listagem de combatentes por tipo e dono com soft delete
    _create_index_if_missing(
        bind,
        "combatentes",
        "ix_combatentes_tipo_deleted_dono",
        ["tipo", "deleted_at", "dono_id"],
    )


def downgrade() -> None:
    bind = op.get_bind()

    index_drop_order = [
        ("combatentes", "ix_combatentes_tipo_deleted_dono"),
        ("talentos", "ix_talentos_ativo_deleted_nome"),
        ("equipamentos", "ix_equipamentos_ativo_deleted_nome"),
        ("grimorio_magias", "ix_grimorio_magias_combatente_classe_adicionada"),
        ("magias_preparadas", "ix_magias_preparadas_combatente_slot_magia"),
        ("magias_slots", "ix_magias_slots_combatente_nivel"),
        ("magias_classes", "ix_magias_classes_classe_nivel_magia"),
        ("pericia_jogadores", "ix_pericia_jogadores_combatente_pericia"),
        ("pericias_classes", "ix_pericias_classes_classe_nome_pericia"),
    ]

    for table_name, index_name in index_drop_order:
        if _index_exists(bind, table_name, index_name):
            op.drop_index(index_name, table_name=table_name)
