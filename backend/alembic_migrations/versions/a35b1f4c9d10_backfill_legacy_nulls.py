"""backfill_legacy_nulls

Revision ID: a35b1f4c9d10
Revises: f2a7b1c4d9e0
Create Date: 2026-03-29 01:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a35b1f4c9d10"
down_revision: Union[str, None] = "f2a7b1c4d9e0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _table_exists(bind, table_name: str) -> bool:
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def _column_exists(bind, table_name: str, column_name: str) -> bool:
    inspector = sa.inspect(bind)
    if table_name not in inspector.get_table_names():
        return False
    columns = [c["name"] for c in inspector.get_columns(table_name)]
    return column_name in columns


def _exec_if_column(bind, table_name: str, column_name: str, sql: str) -> None:
    if _column_exists(bind, table_name, column_name):
        bind.execute(sa.text(sql))


def apply_backfill(bind) -> None:
    if _table_exists(bind, "combatentes"):
        _exec_if_column(bind, "combatentes", "iniciativa", "UPDATE combatentes SET iniciativa = 0 WHERE iniciativa IS NULL")
        _exec_if_column(bind, "combatentes", "ca", "UPDATE combatentes SET ca = 10 WHERE ca IS NULL")
        _exec_if_column(bind, "combatentes", "toque", "UPDATE combatentes SET toque = 10 WHERE toque IS NULL")
        _exec_if_column(bind, "combatentes", "surpresa", "UPDATE combatentes SET surpresa = 10 WHERE surpresa IS NULL")

        _exec_if_column(bind, "combatentes", "fortitude", "UPDATE combatentes SET fortitude = 0 WHERE fortitude IS NULL")
        _exec_if_column(bind, "combatentes", "reflexos", "UPDATE combatentes SET reflexos = 0 WHERE reflexos IS NULL")
        _exec_if_column(bind, "combatentes", "vontade", "UPDATE combatentes SET vontade = 0 WHERE vontade IS NULL")

        _exec_if_column(bind, "combatentes", "forca", "UPDATE combatentes SET forca = 10 WHERE forca IS NULL")
        _exec_if_column(bind, "combatentes", "destreza", "UPDATE combatentes SET destreza = 10 WHERE destreza IS NULL")
        _exec_if_column(bind, "combatentes", "constituicao", "UPDATE combatentes SET constituicao = 10 WHERE constituicao IS NULL")
        _exec_if_column(bind, "combatentes", "inteligencia", "UPDATE combatentes SET inteligencia = 10 WHERE inteligencia IS NULL")
        _exec_if_column(bind, "combatentes", "sabedoria", "UPDATE combatentes SET sabedoria = 10 WHERE sabedoria IS NULL")
        _exec_if_column(bind, "combatentes", "carisma", "UPDATE combatentes SET carisma = 10 WHERE carisma IS NULL")

        _exec_if_column(bind, "combatentes", "nivel", "UPDATE combatentes SET nivel = 1 WHERE nivel IS NULL")
        _exec_if_column(bind, "combatentes", "pontos", "UPDATE combatentes SET pontos = 0 WHERE pontos IS NULL")

        _exec_if_column(bind, "combatentes", "raca", "UPDATE combatentes SET raca = '' WHERE raca IS NULL")
        _exec_if_column(bind, "combatentes", "pagina_referencia", "UPDATE combatentes SET pagina_referencia = '' WHERE pagina_referencia IS NULL")
        _exec_if_column(bind, "combatentes", "classe", "UPDATE combatentes SET classe = 'Sem classe' WHERE classe IS NULL OR TRIM(classe) = ''")

        _exec_if_column(bind, "combatentes", "hp_maximo", "UPDATE combatentes SET hp_maximo = 1 WHERE hp_maximo IS NULL OR hp_maximo <= 0")
        _exec_if_column(bind, "combatentes", "hp_atual", "UPDATE combatentes SET hp_atual = 0 WHERE hp_atual IS NULL OR hp_atual < 0")
        if _column_exists(bind, "combatentes", "hp_atual") and _column_exists(bind, "combatentes", "hp_maximo"):
            bind.execute(sa.text("UPDATE combatentes SET hp_atual = hp_maximo WHERE hp_atual > hp_maximo"))

        _exec_if_column(
            bind,
            "combatentes",
            "tipo",
            """
            UPDATE combatentes
            SET tipo = LOWER(COALESCE(tipo, 'npc'))
            WHERE tipo IS NULL OR LOWER(tipo) NOT IN ('jogador', 'monstro', 'npc')
            """,
        )

        if _column_exists(bind, "combatentes", "dono_id") and _table_exists(bind, "usuarios"):
            owner_id = bind.execute(
                sa.text(
                    """
                    SELECT id
                    FROM usuarios
                    WHERE perfil = 'administrador' AND ativo = 1
                    ORDER BY id
                    LIMIT 1
                    """
                )
            ).scalar()

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
                    sa.text("UPDATE combatentes SET dono_id = :owner_id WHERE dono_id IS NULL"),
                    {"owner_id": owner_id},
                )

    _exec_if_column(bind, "usuarios", "ativo", "UPDATE usuarios SET ativo = TRUE WHERE ativo IS NULL")
    _exec_if_column(bind, "magias", "ativo", "UPDATE magias SET ativo = TRUE WHERE ativo IS NULL")

    _exec_if_column(bind, "equipamentos", "ativo", "UPDATE equipamentos SET ativo = TRUE WHERE ativo IS NULL")
    _exec_if_column(
        bind,
        "equipamentos",
        "criado_em",
        "UPDATE equipamentos SET criado_em = CURRENT_TIMESTAMP WHERE criado_em IS NULL",
    )

    _exec_if_column(bind, "talentos", "ativo", "UPDATE talentos SET ativo = TRUE WHERE ativo IS NULL")
    _exec_if_column(
        bind,
        "talentos",
        "criado_em",
        "UPDATE talentos SET criado_em = CURRENT_TIMESTAMP WHERE criado_em IS NULL",
    )

    _exec_if_column(bind, "pericias", "requer_treinamento", "UPDATE pericias SET requer_treinamento = 0 WHERE requer_treinamento IS NULL")
    _exec_if_column(
        bind,
        "pericias",
        "pode_usar_sem_treinamento",
        "UPDATE pericias SET pode_usar_sem_treinamento = 1 WHERE pode_usar_sem_treinamento IS NULL",
    )
    _exec_if_column(
        bind,
        "pericias",
        "sofre_penalidade_armadura",
        "UPDATE pericias SET sofre_penalidade_armadura = 0 WHERE sofre_penalidade_armadura IS NULL",
    )

    _exec_if_column(bind, "combatente_condicoes", "duracao_turnos", "UPDATE combatente_condicoes SET duracao_turnos = -1 WHERE duracao_turnos IS NULL")
    _exec_if_column(bind, "magias_preparadas", "usada", "UPDATE magias_preparadas SET usada = FALSE WHERE usada IS NULL")

    _exec_if_column(bind, "combates", "turno_atual", "UPDATE combates SET turno_atual = 0 WHERE turno_atual IS NULL")
    _exec_if_column(bind, "combates", "rodada_atual", "UPDATE combates SET rodada_atual = 1 WHERE rodada_atual IS NULL")
    _exec_if_column(bind, "combates", "ativo", "UPDATE combates SET ativo = TRUE WHERE ativo IS NULL")


def upgrade() -> None:
    bind = op.get_bind()
    apply_backfill(bind)


def downgrade() -> None:
    # Backfill é irreversível por definição.
    pass
