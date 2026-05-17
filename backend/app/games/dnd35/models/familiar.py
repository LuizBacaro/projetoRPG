from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class Familiar(Base):
    """Instância de familiar (1:1 com combatente) — Mago / Feiticeiro."""

    __tablename__ = "familiares"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    arena_combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    especie_slug = Column(String(60), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    nivel_mestre = Column(Integer, nullable=False, default=1)
    inteligencia = Column(Integer, nullable=False, default=6)
    armadura_natural_bonus = Column(Integer, nullable=False, default=1)
    hp_atual = Column(Integer, nullable=False, default=1)
    hp_maximo = Column(Integer, nullable=False, default=1)
    ca = Column(Integer, nullable=False, default=10)
    bonus_mestre = Column(String(200), nullable=False, default="")
    habilidades_especiais = Column(JSON, nullable=False, default=list)
    anotacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    combatente = relationship(
        "Combatente",
        back_populates="familiar",
        foreign_keys=[combatente_id],
        lazy="joined",
    )
