"""
database.py
SRP: Configuração SQLAlchemy — gerenciar conexão com banco de dados
SOLID: Configuração centralizada por ambiente (SQLite/PostgreSQL)
"""

import logging
from typing import Generator

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, sessionmaker

from .config import settings

logger = logging.getLogger(__name__)


def _build_engine():
    """
    Monta engine SQLAlchemy conforme o banco configurado.

    Estratégias:
    - SQLite (dev):      check_same_thread=False para ambiente single-thread
    - PostgreSQL (prod): pool management para conexões estáveis em produção

    Returns:
        Engine SQLAlchemy configurado
    """
    is_sqlite = "sqlite" in settings.DATABASE_URL

    engine_config = {
        "url": settings.DATABASE_URL,
        "echo": False,  # ✅ ADICIONADO — trocar para True em dev se precisar de SQL logs
    }

    if is_sqlite:
        engine_config["connect_args"] = {"check_same_thread": False}
        logger.info(f"🔵 Database: SQLite — {settings.DATABASE_URL}")
    else:
        # PostgreSQL: após a migration `fase_c_schemas_auth_dnd35`, tabelas ficam em
        # `auth` e `dnd35`. Os modelos usam nomes não qualificados; sem search_path o
        # Postgres só resolve `public` e falha com "relation does not exist".
        #
        # Não usar `connect_args["options"]=-csearch_path=...`: o pooler da Neon rejeita
        # search_path no pacote de startup. Ajustar com SET após conectar (Neon docs).
        engine_config.update(
            {
                "pool_pre_ping": True,  # testa conexão antes de usar
                "pool_recycle": 300,  # recicla a cada 5 min
                "pool_size": 5,  # máximo de conexões ativas
                "max_overflow": 10,  # conexões extras sob carga
            }
        )
        logger.info(
            "🟢 Database: PostgreSQL — SET search_path após connect (auth,dnd35,public)"
        )

    engine = create_engine(**engine_config)

    if not is_sqlite:

        @event.listens_for(engine, "connect")
        def _postgres_set_search_path(dbapi_conn, connection_record):
            cur = dbapi_conn.cursor()
            cur.execute("SET search_path TO auth, dnd35, public")
            cur.close()

    # ✅ ADICIONADO — listener para melhor logging (opcional)
    if settings.ENVIRONMENT == "development":

        @event.listens_for(engine, "connect")
        def receive_connect(dbapi_conn, connection_record):
            logger.debug(f"✓ Conexão aberta com BD")

        @event.listens_for(engine, "close")
        def receive_close(dbapi_conn, connection_record):
            logger.debug(f"✗ Conexão fechada")

    return engine


# ── Instâncias globais ────────────────────────────────────────────────────────
engine = _build_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=True,  # ✅ ADICIONADO — melhora com lazy loading
)

Base = declarative_base()


# ── Dependency para FastAPI ──────────────────────────────────────────────────
def get_db() -> Generator[Session, None, None]:
    """
    Dependency: Fornece sessão do banco para rotas FastAPI.

    Características:
    - Cria nova sessão a cada request
    - Garante fechamento mesmo com erro (finally)
    - Type hints para melhor IDE support

    Yields:
        Session SQLAlchemy

    Example:
        @app.get("/users")
        def listar_usuarios(db: Session = Depends(get_db)):
            return db.query(Usuario).all()
    """
    db = SessionLocal()
    try:
        yield db
    except HTTPException:
        # Erros HTTP esperados (ex.: 401/403 de autenticação) não são falhas de BD.
        db.rollback()
        raise
    except Exception as e:
        logger.error(f"❌ Erro na sessão do BD: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
