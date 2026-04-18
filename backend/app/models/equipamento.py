"""
equipamento.py
SRP: Modelo ORM para Equipamentos D&D 3.5
SOLID: Single Responsibility — apenas mapeamento de tabela de equipamentos
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from ..core.database import Base
from .mixins import SoftDeleteMixin


class Equipamento(SoftDeleteMixin, Base):
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

    # ── Características da Arma/Equipamento ──
    categoria          = Column(String(50),  nullable=True)  # Armas simples, comuns, exóticas
    subcategoria       = Column(String(100), nullable=True)  # Armas leves – corpo a corpo, etc.
    custo              = Column(String(50),  nullable=True)  # Ex: "2 PO", "5 PP"
    dano_pequeno       = Column(String(20),  nullable=True)  # Dano para criaturas Pequenas
    dano_medio         = Column(String(20),  nullable=True)  # Dano para criaturas Médias
    critico            = Column(String(20),  nullable=True)  # Ex: "×2", "19-20/×2"
    alcance_incremento = Column(String(50),  nullable=True)  # Alcance ou incremento
    peso               = Column(String(20),  nullable=True)  # Ex: "0,5 kg", "2 kg"
    tipo_dano          = Column(String(50),  nullable=True)  # Concussão, Perfurante, Cortante, etc.

    # ── Metadata ──
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ativo     = Column(Boolean, default=True, index=True)

    # ── Relacionamentos ──
    combatentes = relationship(
        "EquipamentoJogador",
        back_populates="equipamento",
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
    adicionado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Relacionamentos ──
    equipamento = relationship("Equipamento", back_populates="combatentes", lazy="joined")
