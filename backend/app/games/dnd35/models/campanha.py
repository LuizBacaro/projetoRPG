"""
Model de Campanha (D&D 3.5)
SRP: representa campanhas criadas por mestres e seus personagens associados.

Canônico em `app.games.dnd35.models.campanha` (campanhas D&D 3.5: mestre,
personagens-combatentes, sessões com resumo D&D).
"""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.core.database import Base


class Campanha(Base):
    __tablename__ = "campanhas"

    id = Column(Integer, primary_key=True, index=True)
    mestre_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=False, index=True
    )
    nome = Column(String(120), nullable=False)
    descricao = Column(String(500), nullable=True, default="")
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    personagens = relationship(
        "Combatente", back_populates="campanha", lazy="selectin"
    )
    sessoes = relationship(
        "SessaoCampanha",
        back_populates="campanha",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
