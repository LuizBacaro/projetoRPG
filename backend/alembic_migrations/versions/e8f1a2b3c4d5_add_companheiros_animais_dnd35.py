"""add_companheiros_animais_dnd35

Revision ID: e8f1a2b3c4d5
Revises: d5e6f7a8b9c0
Create Date: 2026-05-17 12:00:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e8f1a2b3c4d5"
down_revision: Union[str, None] = "d5e6f7a8b9c0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "companheiros_animais"):
        return

    op.create_table(
        "companheiros_animais",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("combatente_id", sa.Integer(), nullable=False),
        sa.Column("especie_slug", sa.String(length=60), nullable=False),
        sa.Column("nome", sa.String(length=120), nullable=False),
        sa.Column("forca", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("destreza", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("constituicao", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("inteligencia", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("sabedoria", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("carisma", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("bonus_atributos", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("hp_atual", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("hp_maximo", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("ca", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("iniciativa", sa.Integer(), nullable=True),
        sa.Column("deslocamento", sa.String(length=80), nullable=True),
        sa.Column("truques", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("talentos", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("pericias", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("ataques", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
        sa.Column("anotacoes", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("atualizado_em", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["combatente_id"], ["combatentes.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("combatente_id", name="uq_companheiros_animais_combatente_id"),
    )
    op.create_index("ix_companheiros_animais_id", "companheiros_animais", ["id"])
    op.create_index(
        "ix_companheiros_animais_combatente_id",
        "companheiros_animais",
        ["combatente_id"],
    )
    op.create_index(
        "ix_companheiros_animais_especie_slug",
        "companheiros_animais",
        ["especie_slug"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    if _table_exists(bind, "companheiros_animais"):
        op.drop_table("companheiros_animais")
