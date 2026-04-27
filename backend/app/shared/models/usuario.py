"""
Model de Usuário
SRP: representa a entidade usuário no banco de dados
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from ...shared.core.database import Base
import enum


class PerfilUsuario(str, enum.Enum):
    ADMINISTRADOR = "administrador"
    MESTRE        = "mestre"
    JOGADOR       = "jogador"


class Usuario(Base):
    __tablename__ = "usuarios"

    id         = Column(Integer, primary_key=True, index=True)
    perfil     = Column(SAEnum(PerfilUsuario), nullable=False)
    nome       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=False)
    ativo      = Column(Boolean, default=True, nullable=False)

    usuario_responsavel = Column(String(150), nullable=True)
    data_acao           = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Usuario id={self.id} email={self.email} perfil={self.perfil}>"