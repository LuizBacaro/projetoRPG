"""Equipamentos Tormenta 20 — catálogo MB + inventário por personagem."""

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


class TormentaEquipamento(Base):
    __tablename__ = "tormenta_equipamentos"
    __table_args__ = (
        UniqueConstraint("nome", name="uq_tormenta_equipamentos_nome"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(200), nullable=False, index=True)
    categoria = Column(String(120), nullable=True)
    secao = Column(String(200), nullable=True)
    custo = Column(String(80), nullable=True)
    dano_p = Column(String(40), nullable=True)
    dano_m = Column(String(40), nullable=True)
    tipo_dano = Column(String(120), nullable=True)
    critico = Column(String(80), nullable=True)
    alcance = Column(String(80), nullable=True)
    peso = Column(String(80), nullable=True)
    descricao = Column(Text, nullable=True)
    pagina_referencia = Column(String(50), nullable=True)
    origem_catalogo_mb = Column(
        Boolean, nullable=False, default=True, server_default="true"
    )
    criado_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    personagens = relationship(
        "TormentaEquipamentoPersonagem",
        back_populates="equipamento",
        lazy="selectin",
    )


class TormentaEquipamentoPersonagem(Base):
    __tablename__ = "tormenta_equipamentos_personagem"
    __table_args__ = (
        UniqueConstraint(
            "personagem_id",
            "equipamento_id",
            name="uq_tormenta_equipamento_personagem_par",
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
    equipamento_id = Column(
        Integer,
        ForeignKey("tormenta_equipamentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantidade = Column(Integer, nullable=False, default=1, server_default="1")
    notas = Column(String(500), nullable=True)
    adicionado_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    personagem = relationship(
        "TormentaPersonagem", back_populates="equipamentos_vinculos"
    )
    equipamento = relationship(
        "TormentaEquipamento", back_populates="personagens", lazy="joined"
    )
