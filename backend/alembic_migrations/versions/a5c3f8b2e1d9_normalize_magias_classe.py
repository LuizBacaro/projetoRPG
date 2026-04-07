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


def upgrade() -> None:
    bind = op.get_bind()

    # Normaliza classe em magias: substitui versões acentuadas pela forma sem acento.
    # Idempotente: uso de WHERE exclui linhas já corretas.
    if bind.dialect.name == "postgresql":
        # PostgreSQL: usa unaccent + upper para normalizar de forma genérica.
        # unaccent extension deve estar instalado (CREATE EXTENSION IF NOT EXISTS unaccent).
        bind.execute(sa.text(
            "UPDATE magias "
            "SET classe = upper(unaccent(classe)) "
            "WHERE classe IS NOT NULL "
            "  AND classe != upper(unaccent(classe))"
        ))
    else:
        # SQLite e outros: aplica substituições explícitas linha a linha.
        # O seed local já normaliza, mas cobre regressões.
        for acentuado, normalizado in _ACENTO_PARA_NORM.items():
            if acentuado != normalizado:
                bind.execute(
                    sa.text("UPDATE magias SET classe = :norm WHERE classe = :acc"),
                    {"norm": normalizado, "acc": acentuado},
                )

    # Aplica o mesmo padrão à tabela magias_classes (caso existam registros futuros).
    if bind.dialect.name == "postgresql":
        bind.execute(sa.text(
            "UPDATE magias_classes "
            "SET classe = upper(unaccent(classe)) "
            "WHERE classe IS NOT NULL "
            "  AND classe != upper(unaccent(classe))"
        ))
    else:
        for acentuado, normalizado in _ACENTO_PARA_NORM.items():
            if acentuado != normalizado:
                bind.execute(
                    sa.text("UPDATE magias_classes SET classe = :norm WHERE classe = :acc"),
                    {"norm": normalizado, "acc": acentuado},
                )


def downgrade() -> None:
    # Não é possível reverter normalização de dados sem backup externo.
    # A operação é segura (semântica preservada) e considerada irreversível.
    pass
