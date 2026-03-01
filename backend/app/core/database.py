"""
Configuração do banco de dados e sessão
SRP: única responsabilidade — gerenciar conexão com o banco
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings


def _build_engine():
    """
    ✅ Monta a engine correta dependendo do banco:
    - SQLite  (dev local): precisa de check_same_thread=False
    - PostgreSQL (Railway): sem connect_args especiais
    """
    is_sqlite = "sqlite" in settings.DATABASE_URL

    connect_args = {"check_same_thread": False} if is_sqlite else {}

    return create_engine(
        settings.DATABASE_URL,
        connect_args=connect_args,
        # ✅ Pool adequado para PostgreSQL no Railway
        pool_pre_ping=True,   # testa conexão antes de usar (evita conexão morta)
        pool_recycle=300,     # recicla conexões a cada 5 min
    )


# Engine
engine = create_engine.__class__  # tipagem — engine criada abaixo
engine = _build_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para models
Base = declarative_base()


def get_db():
    """
    Dependency que fornece a sessão do banco de dados
    Garante fechamento mesmo em caso de erro (context manager)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()