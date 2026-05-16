"""Talentos Tormenta 20 — catálogo + vínculo N:N com personagem (paridade D&D 3.5)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class TormentaTalento(Base):
    """Entrada de catálogo (MB e talentos criados na ficha)."""

    __tablename__ = "tormenta_talentos"
    __table_args__ = (
        UniqueConstraint("nome", name="uq_tormenta_talentos_nome"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    pagina_referencia = Column(String(50), nullable=True)
    origem_catalogo_mb = Column(Boolean, nullable=False, default=True, server_default="true")

    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    personagens = relationship(
        "TormentaTalentoPersonagem",
        back_populates="talento",
        lazy="selectin",
    )


class TormentaTalentoPersonagem(Base):
    """Talento escolhido na ficha de um personagem."""

    __tablename__ = "tormenta_talentos_personagem"
    __table_args__ = (
        UniqueConstraint(
            "personagem_id",
            "talento_id",
            name="uq_tormenta_talento_personagem_par",
        ),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    personagem_id = Column(
        Integer,
        ForeignKey("tormenta_personagens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    talento_id = Column(
        Integer,
        ForeignKey("tormenta_talentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    notas = Column(String(500), nullable=True)
    adicionado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    personagem = relationship("TormentaPersonagem", back_populates="talentos_vinculos")
    talento = relationship("TormentaTalento", back_populates="personagens", lazy="joined")
