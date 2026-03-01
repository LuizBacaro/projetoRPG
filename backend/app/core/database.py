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
    Monta a engine correta dependendo do banco:
    - SQLite  (dev local): precisa de check_same_thread=False
    - PostgreSQL (Railway): pool_pre_ping + pool_recycle para conexões estáveis
    """
    is_sqlite = "sqlite" in settings.DATABASE_URL

    if is_sqlite:
        return create_engine(
            settings.DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

    # ✅ PostgreSQL no Railway — configurações de pool para produção
    return create_engine(
        settings.DATABASE_URL,
        pool_pre_ping=True,  # testa conexão antes de usar (evita conexão morta)
        pool_recycle=300,    # recicla conexões a cada 5 min
        pool_size=5,         # máximo de conexões simultâneas
        max_overflow=10,     # conexões extras permitidas sob carga
    )


# Engine
engine = _build_engine()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para models
Base = declarative_base()


def get_db():
    """
    Dependency que fornece sessão do banco de dados.
    Garante fechamento mesmo em caso de erro.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()