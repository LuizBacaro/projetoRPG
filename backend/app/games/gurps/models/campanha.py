"""Campanha GURPS — isolada das campanhas D&D 3.5."""

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

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


class GurpsCampanhaSolicitacao(Base):
    """Pedido de entrada de um personagem jogador numa campanha GURPS."""

    __tablename__ = "gurps_campanha_solicitacoes"

    id = Column(Integer, primary_key=True, index=True)
    campanha_id = Column(
        Integer,
        ForeignKey("gurps_campanhas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    personagem_id = Column(
        Integer,
        ForeignKey("gurps_personagens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    solicitante_id = Column(
        Integer, ForeignKey("usuarios.id"), nullable=False, index=True
    )
    status = Column(String(20), nullable=False, default="pendente", index=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    resolved_at = Column(DateTime(timezone=True), nullable=True)

    campanha = relationship("GurpsCampanha", lazy="joined")
    personagem = relationship("GurpsPersonagem", lazy="joined")
