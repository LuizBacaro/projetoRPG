"""Modelos do Grimório de magias conhecidas por combatente/classe (D&D 3.5).

Canônico: `app.games.dnd35.models.grimorio`.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class GrimorioMagia(Base):
    __tablename__ = "grimorio_magias"
    __table_args__ = (
        UniqueConstraint(
            "combatente_id",
            "magia_id",
            "classe",
            name="uq_grimorio_combatente_magia_classe",
        ),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    magia_id = Column(
        Integer, ForeignKey("magias.id", ondelete="CASCADE"), nullable=False, index=True
    )
    classe = Column(String(50), nullable=False, index=True)
    favorita = Column(Boolean, nullable=False, default=False)
    anotacoes = Column(Text, nullable=True)
    origem = Column(String(30), nullable=False, default="SELECAO_MANUAL")
    adicionada_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    combatente = relationship("Combatente", lazy="joined")
    magia = relationship("Magia", lazy="joined")


class GrimorioHistoricoTroca(Base):
    __tablename__ = "grimorio_historico_troca"

    id = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    classe = Column(String(50), nullable=False, index=True)
    magia_removida_id = Column(
        Integer,
        ForeignKey("magias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    magia_adicionada_id = Column(
        Integer,
        ForeignKey("magias.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    nivel_personagem = Column(Integer, nullable=False)
    realizada_em = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    combatente = relationship("Combatente", lazy="joined")
    magia_removida = relationship(
        "Magia", foreign_keys=[magia_removida_id], lazy="joined"
    )
    magia_adicionada = relationship(
        "Magia", foreign_keys=[magia_adicionada_id], lazy="joined"
    )


class GrimorioNotificacao(Base):
    __tablename__ = "grimorio_notificacoes"

    id = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="CASCADE"),
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

    combatente = relationship("Combatente", lazy="joined")

    __table_args__ = (
        Index(
            "ix_grimorio_notificacoes_comb_classe_lida",
            "combatente_id",
            "classe",
            "lida",
        ),
        Index(
            "ix_grimorio_notificacoes_comb_classe_tipo",
            "combatente_id",
            "classe",
            "tipo",
        ),
    )
