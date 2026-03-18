"""
Models de Ataque, MagiaSlot e MagiaPreparada
SRP: representa as tabelas no banco
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Ataque(Base):
    __tablename__  = "ataques"
    __table_args__ = {"extend_existing": True}

    id             = Column(Integer, primary_key=True, index=True)
    combatente_id  = Column(Integer, ForeignKey("combatentes.id", ondelete="CASCADE"), nullable=False)
    nome           = Column(String(100), nullable=False)
    bonus_ataque   = Column(String(20),  nullable=False, default="+0")
    dano           = Column(String(30),  nullable=False, default="1d6")
    tipo_dano      = Column(String(50),  nullable=True,  default="")

    combatente = relationship("Combatente", back_populates="ataques")


class MagiaSlot(Base):
    __tablename__  = "magias_slots"
    __table_args__ = {"extend_existing": True}

    id            = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(Integer, ForeignKey("combatentes.id", ondelete="CASCADE"), nullable=False)
    nivel         = Column(Integer, nullable=False)
    total         = Column(Integer, nullable=False, default=0)
    usados        = Column(Integer, nullable=False, default=0)

    combatente = relationship("Combatente", back_populates="magias_slots")


class MagiaPreparada(Base):
    """
    Magia preparada para o dia.
    usada=True → já foi lançada hoje (decrementou slot na arena).
    Reseta ao descanso longo.
    """
    __tablename__  = "magias_preparadas"
    __table_args__ = {"extend_existing": True}

    id            = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(Integer, ForeignKey("combatentes.id", ondelete="CASCADE"), nullable=False)
    magia_id      = Column(Integer, ForeignKey("magias.id",       ondelete="CASCADE"), nullable=False)
    nivel_slot    = Column(Integer, nullable=False)
    usada         = Column(Boolean, nullable=False, default=False)   # ✅ NOVO
    preparada_em  = Column(DateTime, default=datetime.utcnow)

    combatente = relationship("Combatente", back_populates="magias_preparadas")
    magia      = relationship("Magia")