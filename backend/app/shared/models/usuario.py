"""
Model de Usuário
SRP: representa a entidade usuário no banco de dados
"""

import enum

from sqlalchemy import Boolean, Column, DateTime
from sqlalchemy import Enum as SAEnum
from sqlalchemy import Integer, String
from sqlalchemy.sql import func

from ...shared.core.database import Base


class PerfilUsuario(str, enum.Enum):
    ADMINISTRADOR = "administrador"
    # Legado: preferir mestre via campanha (campanhas.mestre_id). Ver ADR 0005.
    MESTRE = "mestre"
    JOGADOR = "jogador"


class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    perfil = Column(SAEnum(PerfilUsuario), nullable=False)
    nome = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=False, index=True)
    senha_hash = Column(String(255), nullable=True)
    oauth_provider = Column(String(32), nullable=True)
    oauth_subject = Column(String(128), nullable=True)
    ativo = Column(Boolean, default=True, nullable=False)

    usuario_responsavel = Column(String(150), nullable=True)
    data_acao = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    def __repr__(self):
        return f"<Usuario id={self.id} email={self.email} perfil={self.perfil}>"
