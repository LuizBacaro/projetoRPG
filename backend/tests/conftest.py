"""
Configuração de fixtures do pytest
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.shared.core.database import Base
import app.models  # noqa: F401 - registra mappers/tabelas no metadata global


@pytest.fixture(scope="function")
def test_db():
    """Fixture que cria um banco de dados em memória para testes"""
    # Criar engine em memória
    engine = create_engine("sqlite:///:memory:")
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    # Criar sessão
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)