"""
Models de Ataque e MagiaSlot
SRP: representa as tabelas de ataques e slots de magia no banco
"""
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base


class Ataque(Base):
    """Ataque vinculado a um combatente."""
    __tablename__  = "ataques"
    __table_args__ = {"extend_existing": True}

    id             = Column(Integer, primary_key=True, index=True)
    combatente_id  = Column(Integer, ForeignKey("combatentes.id", ondelete="CASCADE"), nullable=False)
    nome           = Column(String(100), nullable=False)
    bonus_ataque   = Column(String(20), nullable=False, default="+0")   # ex: "+5", "-1"
    dano           = Column(String(30), nullable=False, default="1d6")  # ex: "1d6+3"
    tipo_dano      = Column(String(50), nullable=True, default="")      # ex: "cortante"

    combatente = relationship("Combatente", back_populates="ataques")


class MagiaSlot(Base):
    """Slot de magia por nível (0–9) vinculado a um combatente."""
    __tablename__  = "magias_slots"
    __table_args__ = {"extend_existing": True}

    id            = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(Integer, ForeignKey("combatentes.id", ondelete="CASCADE"), nullable=False)
    nivel         = Column(Integer, nullable=False)   # 0 a 9
    total         = Column(Integer, nullable=False, default=0)
    usados        = Column(Integer, nullable=False, default=0)

    combatente = relationship("Combatente", back_populates="magias_slots")