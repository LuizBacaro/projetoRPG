from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.shared.core.database import Base
from app.shared.core.mixins import SoftDeleteMixin


class Consumivel(SoftDeleteMixin, Base):
    __tablename__ = "consumiveis"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(120), nullable=False, index=True)
    descricao = Column(String(600), nullable=True)
    pagina_referencia = Column(String(50), nullable=True)
    categoria = Column(String(60), nullable=True)
    tipo = Column(String(60), nullable=True)
    custo = Column(String(50), nullable=True)
    peso = Column(String(30), nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ativo = Column(Boolean, default=True, index=True)

    combatentes = relationship(
        "ConsumivelJogador",
        back_populates="consumivel",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class ConsumivelJogador(Base):
    __tablename__ = "consumiveis_jogador"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    consumivel_id = Column(
        Integer,
        ForeignKey("consumiveis.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantidade = Column(Integer, default=1)
    adicionado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    consumivel = relationship("Consumivel", back_populates="combatentes", lazy="joined")
