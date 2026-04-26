"""
Model de Equipamento (D&D 3.5)
SRP: Modelo ORM para equipamentos do D&D 3.5 (PHB capítulo 7).

Equipamentos PHB 3.5; canônico em `app.games.dnd35.models.equipamento`.
"""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.core.mixins import SoftDeleteMixin


class Equipamento(SoftDeleteMixin, Base):
    """
    Modelo SQLAlchemy para representar um Equipamento do D&D 3.5.

    Colunas baseadas no sistema de equipamentos do PHB 3.5.
    SRP: Única responsabilidade — mapeamento da tabela 'equipamentos'.
    """

    __tablename__ = "equipamentos"
    __table_args__ = {"extend_existing": True}

    # ── Primary Key ──
    id = Column(Integer, primary_key=True, index=True)

    # ── Identificação ──
    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(String(500), nullable=True)
    pagina_referencia = Column(String(50), nullable=True)  # Ex: "PHB p.123"

    # ── Características da Arma/Equipamento ──
    categoria = Column(String(50), nullable=True)
    subcategoria = Column(String(100), nullable=True)
    custo = Column(String(50), nullable=True)
    dano_pequeno = Column(String(20), nullable=True)
    dano_medio = Column(String(20), nullable=True)
    critico = Column(String(20), nullable=True)
    alcance_incremento = Column(String(50), nullable=True)
    peso = Column(String(20), nullable=True)
    tipo_dano = Column(String(50), nullable=True)

    # ── Metadata ──
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ativo = Column(Boolean, default=True, index=True)

    # ── Relacionamentos ──
    combatentes = relationship(
        "EquipamentoJogador",
        back_populates="equipamento",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class EquipamentoJogador(Base):
    """
    Modelo de relacionamento N:N entre Combatente e Equipamento.
    Permite rastrear quais equipamentos cada combatente possui.
    """

    __tablename__ = "equipamentos_jogador"
    __table_args__ = {"extend_existing": True}

    # ── Primary Key ──
    id = Column(Integer, primary_key=True, index=True)

    # ── Foreign Keys ──
    combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    equipamento_id = Column(
        Integer,
        ForeignKey("equipamentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Quantidade ──
    quantidade = Column(Integer, default=1)

    # ── Metadata ──
    adicionado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # ── Relacionamentos ──
    equipamento = relationship(
        "Equipamento", back_populates="combatentes", lazy="joined"
    )
