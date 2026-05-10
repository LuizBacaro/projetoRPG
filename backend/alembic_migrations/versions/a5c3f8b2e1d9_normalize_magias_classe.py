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
    """Sem extensão unaccent: substituições conhecidas (mesmo critério do ramo SQLite)."""
    for acentuado, normalizado in _ACENTO_PARA_NORM.items():
        if acentuado != normalizado:
            bind.execute(
                sa.text(f"UPDATE {table} SET classe = :norm WHERE classe = :acc"),
                {"norm": normalizado, "acc": acentuado},
            )


def _normalize_classe_postgres(bind, table: str) -> None:
    """
    unaccent() só existe após CREATE EXTENSION unaccent (pacote contrib).
    CI / instâncias novas não têm a extensão por padrão; hosts geridos podem
    negar CREATE EXTENSION — nesse caso usa o mapa explícito.
    """
    try:
        bind.execute(sa.text("CREATE EXTENSION IF NOT EXISTS unaccent"))
        bind.execute(
            sa.text(
                f"UPDATE {table} "
                "SET classe = upper(unaccent(classe)) "
                "WHERE classe IS NOT NULL "
                "  AND classe != upper(unaccent(classe))"
            )
        )
    except Exception:
        _normalize_classe_explicit(bind, table)


def upgrade() -> None:
    bind = op.get_bind()

    # Normaliza classe em magias: substitui versões acentuadas pela forma sem acento.
    if bind.dialect.name == "postgresql":
        _normalize_classe_postgres(bind, "magias")
    else:
        _normalize_classe_explicit(bind, "magias")

    if bind.dialect.name == "postgresql":
        _normalize_classe_postgres(bind, "magias_classes")
    else:
        _normalize_classe_explicit(bind, "magias_classes")


def downgrade() -> None:
    # Não é possível reverter normalização de dados sem backup externo.
    # A operação é segura (semântica preservada) e considerada irreversível.
    pass
