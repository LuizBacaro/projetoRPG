"""
Model de Campanha
SRP: representa campanhas criadas por mestres e seus personagens associados.
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..core.database import Base


class Campanha(Base):
    __tablename__ = "campanhas"

    id = Column(Integer, primary_key=True, index=True)
    mestre_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    descricao = Column(String(500), nullable=True, default="")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    personagens = relationship("Combatente", back_populates="campanha", lazy="selectin")
    sessoes = relationship(
        "SessaoCampanha",
        back_populates="campanha",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
