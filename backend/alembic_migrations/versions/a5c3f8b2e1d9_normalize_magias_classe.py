"""normalize_magias_classe

Normaliza magias.classe removendo acentos e convertendo para maiúsculo.
Ex: 'CLÉRIGO' → 'CLERIGO' para garantir compatibilidade com o código de busca
que usa _normalizar() (unicodedata + upper, sem acentos).

Revision ID: a5c3f8b2e1d9
Revises: 2f9b6c4a8e11, 7c1e8b4d9a2f, d5f9a2c1b8e7
Create Date: 2026-04-07 12:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a5c3f8b2e1d9"
down_revision: Union[str, tuple, None] = ("2f9b6c4a8e11", "7c1e8b4d9a2f", "d5f9a2c1b8e7")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Mapeamento explícito: valor acentuado → forma normalizada
# Cobre todas as classes que o seed_magias pode ter inserido com acento.
_ACENTO_PARA_NORM = {
    "CLÉRIGO": "CLERIGO",
    "CLERIGO": "CLERIGO",   # já normalizado — no-op explícito
    "DRUÍDA": "DRUIDA",
    "DRUIDA": "DRUIDA",
    "PALADINO": "PALADINO",
    "RANGER": "RANGER",
    "BARDO": "BARDO",
    "MAGO": "MAGO",
    "FEITICEIRO": "FEITICEIRO",
}


def _normalize_classe_explicit(bind, table: str) -> None:
    """
    Substituições conhecidas em todas as bases.

    Não usamos unaccent nem CREATE EXTENSION no Postgres: se algum comando falha,
    a transação inteira entra em estado abortado; um try/except não corrige isso
    sem SAVEPOINT — o próximo revision falha com InFailedSqlTransaction.
    """
    for acentuado, normalizado in _ACENTO_PARA_NORM.items():
        if acentuado == normalizado:
            continue
        variants = {acentuado, acentuado.upper(), acentuado.lower()}
        for acc in variants:
            bind.execute(
                sa.text(f"UPDATE {table} SET classe = :norm WHERE classe = :acc"),
                {"norm": normalizado, "acc": acc},
            )


def upgrade() -> None:
    bind = op.get_bind()

    _normalize_classe_explicit(bind, "magias")
    _normalize_classe_explicit(bind, "magias_classes")


def downgrade() -> None:
    # Não é possível reverter normalização de dados sem backup externo.
    # A operação é segura (semântica preservada) e considerada irreversível.
    pass
