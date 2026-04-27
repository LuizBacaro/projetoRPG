"""
alembic_migrations/env.py
SRP: Configurar e executar o contexto de migração do Alembic.
"""

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool
from alembic import context

# Configuração do sys.path
backend_root = Path(__file__).parent.parent
sys.path.insert(0, str(backend_root))

# Imports do Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Importa Base e TODOS os models (com try/except para evitar erros)
from app.shared.core.database import Base  # noqa: E402
from app import models as _models  # noqa: F401,E402

# MetaData do Alembic
target_metadata = Base.metadata


def _get_database_url() -> str:
    """Resolve a URL do banco de dados."""
    url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def run_migrations_offline() -> None:
    """Modo offline."""
    url = _get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo online."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = _get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()