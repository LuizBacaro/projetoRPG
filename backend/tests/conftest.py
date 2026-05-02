"""
Configuração de fixtures do pytest
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.shared.core.database import Base
from app.shared.core.security import hash_senha
from app.shared.models.usuario import PerfilUsuario, Usuario
import app.models  # noqa: F401 - registra mappers/tabelas no metadata global


@pytest.fixture(scope="function")
def gurps_personagens_db():
    """SQLite em memória + dois jogadores — usado pelos testes de API GURPS."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        u1 = Usuario(
            perfil=PerfilUsuario.JOGADOR,
            nome="GURPS Um",
            email="gurps1@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        u2 = Usuario(
            perfil=PerfilUsuario.JOGADOR,
            nome="GURPS Dois",
            email="gurps2@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add_all([u1, u2])
        db.commit()
        db.refresh(u1)
        db.refresh(u2)
        yield SessionLocal, u1, u2
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def gurps_mestre_e_jogadores_db():
    """Dois jogadores + mestre — campanhas e cenários que exigem `PerfilUsuario.MESTRE`."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        u1 = Usuario(
            perfil=PerfilUsuario.JOGADOR,
            nome="GURPS J1",
            email="gurps_j1@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        u2 = Usuario(
            perfil=PerfilUsuario.JOGADOR,
            nome="GURPS J2",
            email="gurps_j2@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        mestre = Usuario(
            perfil=PerfilUsuario.MESTRE,
            nome="GURPS Mestre",
            email="gurps_mestre@example.com",
            senha_hash=hash_senha("SenhaSegura123"),
            ativo=True,
        )
        db.add_all([u1, u2, mestre])
        db.commit()
        db.refresh(u1)
        db.refresh(u2)
        db.refresh(mestre)
        yield SessionLocal, mestre, u1, u2
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


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