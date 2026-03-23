"""
alembic/env.py
SRP: única responsabilidade — configurar e executar o contexto de migração.
Lê DATABASE_URL do ambiente (Railway ou .env local).
"""
import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# 
# 1. Garante que o pacote app/ seja encontrado independente de onde o
#    alembic é chamado (ex: cd backend && alembic upgrade head)
# 
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 
# 2. Importa todos os models para que o Base.metadata os conheça.
#    OCP: adicionar novos models aqui sem alterar lógica de migração.
# 
from app.core.database import Base  # noqa: E402  — Base com metadata

# Importa cada model explicitamente para que o SQLAlchemy registre as tabelas
from app.models.usuario    import Usuario     # noqa: F401
from app.models.combatente import Combatente  # noqa: F401

# Tenta importar models opcionais (Ataque, MagiaSlot) sem quebrar se não existirem
try:
    from app.models.ataque     import Ataque      # noqa: F401
    from app.models.magia_slot import MagiaSlot   # noqa: F401
except ImportError:
    pass

# 
# 3. Configuração do Alembic
# 
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData que o Alembic usará para autogenerate
target_metadata = Base.metadata


# 
# 4. Helpers
# 
def _get_database_url() -> str:
    """
    DIP: resolve a URL do banco de dados a partir do ambiente.
    Prioridade: variável de ambiente DATABASE_URL > alembic.ini.
    Converte 'postgres://' (Heroku/Railway legado) para 'postgresql://'.
    """
    url = os.environ.get("DATABASE_URL") or config.get_main_option("sqlalchemy.url")
    if url and url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url


def run_migrations_offline() -> None:
    """
    Modo offline: gera SQL puro sem conexão ativa.
    Útil para revisar o SQL antes de aplicar em produção.
    """
    url = _get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,       # detecta mudanças de tipo
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Modo online: aplica migrações com conexão ativa ao banco.
    Configurações de pool alinhadas com database.py para Railway.
    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = _get_database_url()

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,  # sem pool no alembic — cada run cria/fecha conexão
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


# 
# 5. Entry point
# 
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()