"""Campanhas e sessões Tormenta 20 — paridade com D&D 3.5 / GURPS."""

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    false,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.core.database import Base


class TormentaCampanha(Base):
    __tablename__ = "tormenta_campanhas"

    id = Column(Integer, primary_key=True, index=True)
    mestre_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    descricao = Column(String(500), nullable=True, default="")
    regras_opcionais_ativas = Column(JSON, nullable=True, default=list)
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
        "TormentaPersonagem",
        back_populates="campanha",
        lazy="selectin",
    )
    sessoes = relationship(
        "TormentaSessaoCampanha",
        back_populates="campanha",
        lazy="selectin",
        cascade="all, delete-orphan",
    )


class TormentaSessaoCampanha(Base):
    __tablename__ = "tormenta_campanhas_sessoes"

    id = Column(Integer, primary_key=True, index=True)
    campanha_id = Column(
        Integer,
        ForeignKey("tormenta_campanhas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resumo = Column(String(4000), nullable=False)
    visivel_jogadores = Column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    campanha = relationship("TormentaCampanha", back_populates="sessoes", lazy="joined")
