"""hp_negativo_regras_morte

Permite hp_atual negativo (até -10) para implementar regras D&D 3.5 de
morte/estabilização. Monstros morrem a 0 HP; Jogadores/NPCs morrem a -10 HP.

Revision ID: d5f9a2c1b8e7
Revises: 5e72b9a1c4d0
Create Date: 2026-04-06 00:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d5f9a2c1b8e7"
down_revision: Union[str, None] = "5e72b9a1c4d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    try:
        bind = op.get_bind()
        return bind.dialect.name == "sqlite"
    except Exception:
        return False


def upgrade() -> None:
    if _is_sqlite():
        # SQLite não suporta DROP/ADD CONSTRAINT — no-op seguro.
        return

    bind = op.get_bind()

    # Garante que nenhum registro tenha hp_atual abaixo de -10 (dados legados
    # sempre terão hp_atual ≥ 0, então esta linha é apenas de segurança).
    bind.execute(sa.text("UPDATE combatentes SET hp_atual = -10 WHERE hp_atual < -10"))

    # Remove constraint antiga que forçava hp_atual >= 0
    op.drop_constraint(
        "ck_combatentes_hp_atual_non_negative",
        "combatentes",
        type_="check",
    )

    # Remove constraint que limita hp_atual <= hp_maximo pois hp negativo
    # é sempre <= hp_maximo, mas a constraint antiga foi gerada sem contemplar
    # valores negativos. Recria com mesmo nome para manter compatibilidade.
    try:
        op.drop_constraint(
            "ck_combatentes_hp_atual_lte_hp_maximo",
            "combatentes",
            type_="check",
        )
    except Exception:
        pass  # Pode não existir em bancos que não rodaram c1b7e4d2a9f0

    # Nova constraint: permite -10 a hp_maximo
    op.create_check_constraint(
        "ck_combatentes_hp_atual_minimum",
        "combatentes",
        "hp_atual >= -10",
    )
    op.create_check_constraint(
        "ck_combatentes_hp_atual_lte_hp_maximo",
        "combatentes",
        "hp_atual <= hp_maximo",
    )


def downgrade() -> None:
    if _is_sqlite():
        return

    bind = op.get_bind()

    # Seta hp negativo para 0 antes de restaurar constraint >= 0
    bind.execute(sa.text("UPDATE combatentes SET hp_atual = 0 WHERE hp_atual < 0"))

    op.drop_constraint("ck_combatentes_hp_atual_minimum", "combatentes", type_="check")
    try:
        op.drop_constraint(
            "ck_combatentes_hp_atual_lte_hp_maximo", "combatentes", type_="check"
        )
    except Exception:
        pass

    op.create_check_constraint(
        "ck_combatentes_hp_atual_non_negative",
        "combatentes",
        "hp_atual >= 0",
    )
    op.create_check_constraint(
        "ck_combatentes_hp_atual_lte_hp_maximo",
        "combatentes",
        "hp_atual <= hp_maximo",
    )
