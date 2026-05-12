"""
armadura_protecao.py
SRP: modelos ORM para catálogo e vínculo de armaduras/itens de proteção do personagem
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class ArmaduraProtecao(Base):
    """Catálogo de armaduras/itens de proteção disponíveis."""

    __tablename__ = "armaduras_protecao"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False, index=True)
    tipo = Column(String(60), nullable=False, default="Armadura")
    bonus_ca = Column(Integer, nullable=False, default=0)
    des_max = Column(String(20), nullable=True)
    penalidade = Column(Integer, nullable=False, default=0)
    falha_arcana = Column(String(20), nullable=True)
    deslocamento = Column(String(40), nullable=True)
    peso = Column(Float, nullable=True)
    propriedades_especiais = Column(String(600), nullable=True)
    ativo = Column(Boolean, nullable=False, default=True, index=True)
    criado_em = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    combatentes = relationship(
        "ArmaduraProtecaoJogador",
        back_populates="item",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ArmaduraProtecaoJogador(Base):
    """Vínculo N:N entre combatente e item de proteção."""

    __tablename__ = "armaduras_protecao_jogador"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    item_id = Column(
        Integer,
        ForeignKey("armaduras_protecao.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    adicionado_em = Column(
        DateTime, nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    item = relationship("ArmaduraProtecao", back_populates="combatentes", lazy="joined")
