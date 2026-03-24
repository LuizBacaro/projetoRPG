"""
equipamento.py
SRP: Modelo ORM para Equipamentos D&D 3.5
SOLID: Single Responsibility — apenas mapeamento de tabela de equipamentos
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base


class Equipamento(Base):
    """
    Modelo SQLAlchemy para representar um Equipamento do D&D 3.5.
    
    Colunas baseadas no sistema de equipamentos do PHB 3.5.
    SRP: Única responsabilidade — mapeamento da tabela 'equipamentos'.
    """

    __tablename__ = 'equipamentos'
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
        "EquipamentoJogador",
        cascade="all, delete-orphan",
        lazy="selectin"
    )


class EquipamentoJogador(Base):
    """
    Modelo de relacionamento N:N entre Combatente e Equipamento.
    Permite rastrear quais equipamentos cada combatente possui.
    """

    __tablename__ = 'equipamentos_jogador'
    __table_args__ = {'extend_existing': True}

    # ── Primary Key ──
    id = Column(Integer, primary_key=True, index=True)

    # ── Foreign Keys ──
    combatente_id   = Column(Integer, ForeignKey('combatentes.id', ondelete='CASCADE'), nullable=False, index=True)
    equipamento_id  = Column(Integer, ForeignKey('equipamentos.id', ondelete='CASCADE'), nullable=False, index=True)

    # ── Quantidade ──
    quantidade = Column(Integer, default=1)

    # ── Metadata ──
    adicionado_em = Column(DateTime, default=datetime.utcnow)

    # ── Relacionamentos ──
    equipamento = relationship("Equipamento", lazy="joined")
