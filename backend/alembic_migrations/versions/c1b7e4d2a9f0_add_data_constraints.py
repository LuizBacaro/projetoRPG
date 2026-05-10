"""add_data_constraints

Revision ID: c1b7e4d2a9f0
Revises: 9f3c2f7b1a01
Create Date: 2026-03-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1b7e4d2a9f0"
down_revision: Union[str, None] = "9f3c2f7b1a01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _tabela_existe(nome: str) -> bool:
    try:
        bind = op.get_bind()
        if hasattr(bind, "__class__") and "Mock" in bind.__class__.__name__:
            return False
        return nome in sa.inspect(bind).get_table_names()
    except Exception:
        return False


def upgrade() -> None:
    bind = op.get_bind()

    # Normaliza dados antes de aplicar constraints
    bind.execute(sa.text("UPDATE combatentes SET hp_maximo = 1 WHERE hp_maximo IS NULL OR hp_maximo <= 0"))
    bind.execute(sa.text("UPDATE combatentes SET hp_atual = 0 WHERE hp_atual IS NULL OR hp_atual < 0"))
    bind.execute(sa.text("UPDATE combatentes SET hp_atual = hp_maximo WHERE hp_atual > hp_maximo"))
    bind.execute(
        sa.text(
            """
            UPDATE combatentes
            SET tipo = LOWER(COALESCE(tipo, 'npc'))
            WHERE tipo IS NULL OR LOWER(tipo) NOT IN ('jogador', 'monstro', 'npc')
            """
        )
    )

    # Remove duplicatas de magias preparadas (mantém menor id)
    if _tabela_existe("magias_preparadas"):
        bind.execute(
            sa.text(
                """
                DELETE FROM magias_preparadas
                WHERE id IN (
                    SELECT id FROM (
                        SELECT
                            id,
                            ROW_NUMBER() OVER (
                                PARTITION BY combatente_id, magia_id
                                ORDER BY id
                            ) AS rn
                        FROM magias_preparadas
                    ) t
                    WHERE t.rn > 1
                )
                """
            )
        )

    with op.batch_alter_table("combatentes") as batch_op:
        batch_op.create_check_constraint(
            "ck_combatentes_hp_atual_non_negative",
            "hp_atual >= 0",
        )
        batch_op.create_check_constraint(
            "ck_combatentes_hp_maximo_positive",
            "hp_maximo > 0",
        )
        batch_op.create_check_constraint(
            "ck_combatentes_hp_atual_lte_hp_maximo",
            "hp_atual <= hp_maximo",
        )
        batch_op.create_check_constraint(
            "ck_combatentes_tipo_valido",
            "tipo IN ('jogador', 'monstro', 'npc')",
        )

    if _tabela_existe("magias_preparadas"):
        with op.batch_alter_table("magias_preparadas") as batch_op:
            batch_op.create_unique_constraint(
                "uq_magias_preparadas_combatente_magia",
                ["combatente_id", "magia_id"],
            )


def downgrade() -> None:
    if _tabela_existe("magias_preparadas"):
        with op.batch_alter_table("magias_preparadas") as batch_op:
            batch_op.drop_constraint("uq_magias_preparadas_combatente_magia", type_="unique")

    with op.batch_alter_table("combatentes") as batch_op:
        batch_op.drop_constraint("ck_combatentes_tipo_valido", type_="check")
        batch_op.drop_constraint("ck_combatentes_hp_atual_lte_hp_maximo", type_="check")
        batch_op.drop_constraint("ck_combatentes_hp_maximo_positive", type_="check")
        batch_op.drop_constraint("ck_combatentes_hp_atual_non_negative", type_="check")
