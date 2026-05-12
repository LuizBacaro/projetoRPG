"""
CI (Postgres vazio): aplica o schema atual via SQLAlchemy e marca Alembic em head.

A cadeia incremental assume baseline legado; `upgrade head` em BD sem tabelas quebra.
Este caminho alinha o banco de testes ao modelo atual e sincroniza `alembic_version`,
mantendo os passos seguintes (`upgrade head` idempotente, heads único).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, event

_backend_root = Path(__file__).resolve().parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

import app.models  # noqa: F401,E402
from app.shared.core.database import Base  # noqa: E402


def main() -> None:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise SystemExit("DATABASE_URL não definido")

    engine = create_engine(url)

    if "postgresql" in url:
        # Igual ao runtime FastAPI / env Alembic (Neon não aceita search_path no startup URL).
        @event.listens_for(engine, "connect")
        def _set_search_path(dbapi_conn, _connection_record):
            cur = dbapi_conn.cursor()
            cur.execute("SET search_path TO auth, dnd35, public")
            cur.close()

    Base.metadata.create_all(bind=engine)

    from alembic import command
    from alembic.config import Config

    cfg = Config(str(_backend_root / "alembic.ini"))
    command.stamp(cfg, "head")


if __name__ == "__main__":
    main()
