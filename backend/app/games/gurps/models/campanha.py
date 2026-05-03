"""Campanha GURPS — isolada das campanhas D&D 3.5."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.core.database import Base


class GurpsCampanha(Base):
    __tablename__ = "gurps_campanhas"

    id = Column(Integer, primary_key=True, index=True)
    mestre_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
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
        "GurpsPersonagem",
        back_populates="campanha",
        lazy="selectin",
    )
    sessoes = relationship(
        "GurpsSessaoCampanha",
        back_populates="campanha",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
