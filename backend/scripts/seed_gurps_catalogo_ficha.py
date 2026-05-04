"""
Popula as tabelas `gurps_catalogo_ficha_*` a partir da mesma união usada pelos JSON (Lite + sumário PDF).

Depois disso, GET /api/v1/gurps/personagens/catalogo/lite-ficha lê listas do banco (meta continua vinda dos arquivos).

Uso:
  cd backend && DATABASE_URL='postgresql://...' python scripts/seed_gurps_catalogo_ficha.py

SQLite local (após `alembic upgrade head` ou tabelas criadas pelo app):
  cd backend && python scripts/seed_gurps_catalogo_ficha.py
"""

from __future__ import annotations

import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from sqlalchemy import inspect  # noqa: E402

from app.games.gurps.repositories.catalogo_ficha_repository import (  # noqa: E402
    repopular_catalogo_ficha_de_arquivos,
)
from app.shared.core.database import SessionLocal  # noqa: E402

_TABELAS = (
    "gurps_catalogo_ficha_vantagens",
    "gurps_catalogo_ficha_desvantagens",
    "gurps_catalogo_ficha_pericias",
)


def main() -> int:
    db = SessionLocal()
    try:
        existentes = set(inspect(db.get_bind()).get_table_names())
        faltando = [t for t in _TABELAS if t not in existentes]
        if faltando:
            print(
                "As tabelas do catálogo ainda não existem neste banco "
                f"(faltando: {', '.join(faltando)}).\n"
                "Rode antes, com o mesmo DATABASE_URL:\n"
                "  python3 -m alembic upgrade head"
            )
            return 1
        nv, nd, np = repopular_catalogo_ficha_de_arquivos(db)
        db.commit()
        print(f"Catálogo GURPS ficha gravado: {nv} vantagens, {nd} desvantagens, {np} perícias.")
        return 0
    except Exception as e:
        db.rollback()
        print(f"Erro: {e}")
        return 1
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
