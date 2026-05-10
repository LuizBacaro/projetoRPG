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


def _nome_constraint_igual(registrado: str | None, esperado: str) -> bool:
    return (registrado or "").lower() == esperado.lower()


def _check_constraint_existe(tabela: str, nome: str) -> bool:
    try:
        bind = op.get_bind()
        insp = sa.inspect(bind)
        if tabela not in insp.get_table_names():
            return False
        return any(
            _nome_constraint_igual(c.get("name"), nome)
            for c in insp.get_check_constraints(tabela)
        )
    except Exception:
        return False


def _unique_constraint_existe(tabela: str, nome: str) -> bool:
    try:
        bind = op.get_bind()
        insp = sa.inspect(bind)
        if tabela not in insp.get_table_names():
            return False
        return any(
            _nome_constraint_igual(u.get("name"), nome)
            for u in insp.get_unique_constraints(tabela)
        )
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

    # Schema criado por metadata/create_all já traz várias checks com estes nomes.
    combatentes_checks = [
        ("ck_combatentes_hp_atual_non_negative", "hp_atual >= 0"),
        ("ck_combatentes_hp_maximo_positive", "hp_maximo > 0"),
        ("ck_combatentes_hp_atual_lte_hp_maximo", "hp_atual <= hp_maximo"),
        ("ck_combatentes_tipo_valido", "tipo IN ('jogador', 'monstro', 'npc')"),
    ]
    pending_ck = [
        (n, sql)
        for n, sql in combatentes_checks
        if not _check_constraint_existe("combatentes", n)
    ]
    if pending_ck:
        with op.batch_alter_table("combatentes") as batch_op:
            for nome, sql_chk in pending_ck:
                batch_op.create_check_constraint(nome, sql_chk)

    if _tabela_existe("magias_preparadas"):
        if not _unique_constraint_existe(
            "magias_preparadas", "uq_magias_preparadas_combatente_magia"
        ):
            with op.batch_alter_table("magias_preparadas") as batch_op:
                batch_op.create_unique_constraint(
                    "uq_magias_preparadas_combatente_magia",
                    ["combatente_id", "magia_id"],
                )


def downgrade() -> None:
    if _tabela_existe("magias_preparadas") and _unique_constraint_existe(
        "magias_preparadas", "uq_magias_preparadas_combatente_magia"
    ):
        with op.batch_alter_table("magias_preparadas") as batch_op:
            batch_op.drop_constraint("uq_magias_preparadas_combatente_magia", type_="unique")

    drop_order = [
        "ck_combatentes_tipo_valido",
        "ck_combatentes_hp_atual_lte_hp_maximo",
        "ck_combatentes_hp_maximo_positive",
        "ck_combatentes_hp_atual_non_negative",
    ]
    pending_drop = [n for n in drop_order if _check_constraint_existe("combatentes", n)]
    if pending_drop:
        with op.batch_alter_table("combatentes") as batch_op:
            for nome in pending_drop:
                batch_op.drop_constraint(nome, type_="check")
