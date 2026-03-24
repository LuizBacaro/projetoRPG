"""
talento.py
SRP: Modelo ORM para Talentos D&D 3.5
SOLID: Single Responsibility — apenas mapeamento de tabela de talentos
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Talento(Base):
    """
    Modelo SQLAlchemy para representar um Talento do D&D 3.5.
    
    Colunas baseadas no sistema de talentos do PHB 3.5.
    SRP: Única responsabilidade — mapeamento da tabela 'talentos'.
    """

    __tablename__ = 'talentos'
    __table_args__ = {'extend_existing': True}

    # ── Primary Key ──
    id = Column(Integer, primary_key=True, index=True)

    # ── Identificação ──
    nome               = Column(String(100), nullable=False, index=True)
    descricao          = Column(String(500), nullable=True)
    pagina_referencia  = Column(String(50),  nullable=True)  # Ex: "PHB p.123"

    # ── Metadata ──
    criado_em = Column(DateTime, default=datetime.utcnow)
    ativo     = Column(Boolean, default=True, index=True)

    # ── Relacionamentos ──
    combatentes = relationship(
        "TalentoJogador",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class TalentoJogador(Base):
    """
    Modelo de relacionamento N:N entre Combatente e Talento.
    Permite rastrear quais talentos cada combatente possui.
    """

    __tablename__ = 'talentos_jogador'
    __table_args__ = {'extend_existing': True}

    # ── Primary Key ──
    id = Column(Integer, primary_key=True, index=True)

    # ── Foreign Keys ──
    combatente_id   = Column(Integer, ForeignKey('combatentes.id', ondelete='CASCADE'), nullable=False, index=True)
    talento_id      = Column(Integer, ForeignKey('talentos.id', ondelete='CASCADE'), nullable=False, index=True)

    # ── Metadata ──
    adicionado_em = Column(DateTime, default=datetime.utcnow)

    # ── Relacionamentos ──
    talento = relationship("Talento", lazy="joined")
