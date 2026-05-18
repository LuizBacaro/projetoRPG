"""Grimório D&D 5e — magias conhecidas/preparadas por personagem."""

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


class Dnd5eGrimorioMagia(Base):
    __tablename__ = "dnd5e_grimorio_magias"
    __table_args__ = (
        UniqueConstraint(
            "personagem_id",
            "magia_id",
            "classe",
            name="uq_dnd5e_grimorio_personagem_magia_classe",
        ),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    personagem_id = Column(
        Integer,
        ForeignKey("dnd5e_personagens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    magia_id = Column(
        Integer,
        ForeignKey("dnd5e_magias.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    classe = Column(String(50), nullable=False, index=True)
    favorita = Column(Boolean, nullable=False, default=False)
    anotacoes = Column(Text, nullable=True)
    origem = Column(String(30), nullable=False, default="SELECAO_MANUAL")
    adicionada_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    personagem = relationship("Dnd5ePersonagem", lazy="joined")
    magia = relationship("Dnd5eMagia", lazy="joined")


class Dnd5eGrimorioHistoricoTroca(Base):
    __tablename__ = "dnd5e_grimorio_historico_troca"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    personagem_id = Column(
        Integer,
        ForeignKey("dnd5e_personagens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    classe = Column(String(50), nullable=False, index=True)
    magia_removida_id = Column(
        Integer,
        ForeignKey("dnd5e_magias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    magia_adicionada_id = Column(
        Integer,
        ForeignKey("dnd5e_magias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    nivel_personagem = Column(Integer, nullable=False)
    realizada_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    magia_removida = relationship(
        "Dnd5eMagia", foreign_keys=[magia_removida_id], lazy="joined"
    )
    magia_adicionada = relationship(
        "Dnd5eMagia", foreign_keys=[magia_adicionada_id], lazy="joined"
    )


class Dnd5eGrimorioNotificacao(Base):
    __tablename__ = "dnd5e_grimorio_notificacoes"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    personagem_id = Column(
        Integer,
        ForeignKey("dnd5e_personagens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    classe = Column(String(50), nullable=False, index=True)
    tipo = Column(String(40), nullable=False, index=True)
    dados = Column(Text, nullable=True)
    lida = Column(Boolean, nullable=False, default=False)
    criada_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
