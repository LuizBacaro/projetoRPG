"""Remove constraint legada ck_combatentes_hp_atual_non_negative.

Revisão de fix da migration `d5f9a2c1b8e7_hp_negativo_regras_morte`, que no
SQLite fazia `return` (no-op) e deixou a constraint antiga `hp_atual >= 0`
ativa em bancos locais. Em Postgres, recém-promovidos a partir de SQLite ou
bancos onde o `drop_constraint` original tenha falhado silenciosamente, a
constraint também pode ter sobrevivido. Esta migration é idempotente.

Sintoma sem este fix: `IntegrityError: CHECK constraint failed:
ck_combatentes_hp_atual_non_negative` ao aplicar dano em PJ/NPC com HP a 0
(D&D 3.5 permite jogador chegar a -10 antes de morrer).

Revision ID: c4e8d2a9f1b3
Revises: a3b4c5d6e7f8
Create Date: 2026-05-09
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c4e8d2a9f1b3"
down_revision: Union[str, None] = "a3b4c5d6e7f8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


_CONSTRAINT_LEGADA = "ck_combatentes_hp_atual_non_negative"
_CONSTRAINT_NOVA_MIN = "ck_combatentes_hp_atual_minimum"
_CONSTRAINT_LTE = "ck_combatentes_hp_atual_lte_hp_maximo"
_CONSTRAINT_TIPO = "ck_combatentes_tipo_valido"
_CONSTRAINT_HPMAX = "ck_combatentes_hp_maximo_positive"


def _dialect_name() -> str:
    try:
        return op.get_bind().dialect.name
    except Exception:
        return ""


def upgrade() -> None:
    bind = op.get_bind()
    dialect = _dialect_name()

    bind.execute(
        sa.text("UPDATE combatentes SET hp_atual = -10 WHERE hp_atual < -10")
    )

    if dialect == "sqlite":
        with op.batch_alter_table("combatentes", recreate="always") as batch_op:
            try:
                batch_op.drop_constraint(_CONSTRAINT_LEGADA, type_="check")
            except Exception:
                pass
        return

    if dialect == "postgresql":
        bind.execute(
            sa.text(
                f'ALTER TABLE combatentes DROP CONSTRAINT IF EXISTS "{_CONSTRAINT_LEGADA}"'
            )
        )
        bind.execute(
            sa.text(
                "DO $$ BEGIN "
                f"IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{_CONSTRAINT_NOVA_MIN}') THEN "
                f'ALTER TABLE combatentes ADD CONSTRAINT "{_CONSTRAINT_NOVA_MIN}" CHECK (hp_atual >= -10); '
                "END IF; END $$;"
            )
        )
        return

    try:
        op.drop_constraint(_CONSTRAINT_LEGADA, "combatentes", type_="check")
    except Exception:
        pass


def downgrade() -> None:
    """Recria a constraint legada `hp_atual >= 0`.

    Atenção: zera registros com hp_atual negativo antes de recriar para evitar
    violação imediata. A regra de morte D&D fica indisponível enquanto este
    downgrade estiver ativo.
    """
    bind = op.get_bind()
    dialect = _dialect_name()

    bind.execute(sa.text("UPDATE combatentes SET hp_atual = 0 WHERE hp_atual < 0"))

    if dialect == "sqlite":
        with op.batch_alter_table("combatentes", recreate="always") as batch_op:
            batch_op.create_check_constraint(_CONSTRAINT_LEGADA, "hp_atual >= 0")
        return

    if dialect == "postgresql":
        bind.execute(
            sa.text(
                "DO $$ BEGIN "
                f"IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = '{_CONSTRAINT_LEGADA}') THEN "
                f'ALTER TABLE combatentes ADD CONSTRAINT "{_CONSTRAINT_LEGADA}" CHECK (hp_atual >= 0); '
                "END IF; END $$;"
            )
        )
        return

    op.create_check_constraint(_CONSTRAINT_LEGADA, "combatentes", "hp_atual >= 0")
