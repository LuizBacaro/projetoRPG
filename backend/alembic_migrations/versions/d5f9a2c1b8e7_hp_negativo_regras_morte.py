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


def _nome_ck(registrado: str | None, esperado: str) -> bool:
    return (registrado or "").lower() == esperado.lower()


def _check_constraint_existe(tabela: str, nome: str) -> bool:
    try:
        bind = op.get_bind()
        insp = sa.inspect(bind)
        if tabela not in insp.get_table_names():
            return False
        return any(
            _nome_ck(c.get("name"), nome)
            for c in insp.get_check_constraints(tabela)
        )
    except Exception:
        return False


def _drop_check_se_existir(tabela: str, nome: str) -> None:
    if _check_constraint_existe(tabela, nome):
        op.drop_constraint(nome, tabela, type_="check")


def upgrade() -> None:
    if _is_sqlite():
        # SQLite não suporta DROP/ADD CONSTRAINT — no-op seguro.
        return

    bind = op.get_bind()

    # Garante que nenhum registro tenha hp_atual abaixo de -10 (dados legados
    # sempre terão hp_atual ≥ 0, então esta linha é apenas de segurança).
    bind.execute(sa.text("UPDATE combatentes SET hp_atual = -10 WHERE hp_atual < -10"))

    # Remove constraint antiga que forçava hp_atual >= 0 (pode não existir se veio de metadata).
    _drop_check_se_existir("combatentes", "ck_combatentes_hp_atual_non_negative")

    # Remove LTE para recriar (metadata/create_all pode já ter minimum+LTE com os mesmos nomes).
    _drop_check_se_existir("combatentes", "ck_combatentes_hp_atual_lte_hp_maximo")

    # Nova constraint: permite -10 a hp_maximo (ORM já pode ter criado esta check).
    if not _check_constraint_existe("combatentes", "ck_combatentes_hp_atual_minimum"):
        op.create_check_constraint(
            "ck_combatentes_hp_atual_minimum",
            "combatentes",
            "hp_atual >= -10",
        )
    if not _check_constraint_existe("combatentes", "ck_combatentes_hp_atual_lte_hp_maximo"):
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

    _drop_check_se_existir("combatentes", "ck_combatentes_hp_atual_minimum")
    _drop_check_se_existir("combatentes", "ck_combatentes_hp_atual_lte_hp_maximo")

    if not _check_constraint_existe("combatentes", "ck_combatentes_hp_atual_non_negative"):
        op.create_check_constraint(
            "ck_combatentes_hp_atual_non_negative",
            "combatentes",
            "hp_atual >= 0",
        )
    if not _check_constraint_existe("combatentes", "ck_combatentes_hp_atual_lte_hp_maximo"):
        op.create_check_constraint(
            "ck_combatentes_hp_atual_lte_hp_maximo",
            "combatentes",
            "hp_atual <= hp_maximo",
        )
