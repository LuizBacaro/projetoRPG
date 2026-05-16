"""Consumíveis Tormenta 20 — catálogo + inventário por personagem."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class TormentaConsumivel(Base):
    __tablename__ = "tormenta_consumiveis"
    __table_args__ = (
        UniqueConstraint("nome", name="uq_tormenta_consumiveis_nome"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    categoria = Column(String(80), nullable=True)
    tipo = Column(String(80), nullable=True)
    custo = Column(String(80), nullable=True)
    peso = Column(String(80), nullable=True)
    origem_catalogo_mb = Column(
        Boolean, nullable=False, default=False, server_default="false"
    )
    criado_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    personagens = relationship(
        "TormentaConsumivelPersonagem",
        back_populates="consumivel",
        lazy="selectin",
    )


class TormentaConsumivelPersonagem(Base):
    __tablename__ = "tormenta_consumiveis_personagem"
    __table_args__ = (
        UniqueConstraint(
            "personagem_id",
            "consumivel_id",
            name="uq_tormenta_consumivel_personagem_par",
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
    consumivel_id = Column(
        Integer,
        ForeignKey("tormenta_consumiveis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantidade = Column(Integer, nullable=False, default=1, server_default="1")
    notas = Column(String(500), nullable=True)
    adicionado_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    personagem = relationship(
        "TormentaPersonagem", back_populates="consumiveis_vinculos"
    )
    consumivel = relationship(
        "TormentaConsumivel", back_populates="personagens", lazy="joined"
    )
