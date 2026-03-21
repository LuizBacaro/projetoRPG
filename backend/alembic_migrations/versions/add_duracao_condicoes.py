"""
add_duracao_condicoes.py
Migração: adiciona coluna duracao_turnos em combatente_condicoes
"""
from alembic import op
import sqlalchemy as sa

revision = "add_duracao_condicoes"
down_revision = "002_add_pagina_referencia"  # ✅ CORRIGIDO: referenciar migration anterior
branch_labels = None
depends_on = None

def upgrade() -> None:
    try:
        op.add_column(
            "combatente_condicoes",
            sa.Column(
                "duracao_turnos",
                sa.Integer(),
                nullable=False,
                server_default="-1"
            )
        )
        print("✅ Coluna duracao_turnos adicionada")
    except Exception as e:
        if "already exists" not in str(e).lower():
            raise

def downgrade() -> None:
    try:
        op.drop_column("combatente_condicoes", "duracao_turnos")
        print("↩️ Coluna removida")
    except Exception as e:
        pass