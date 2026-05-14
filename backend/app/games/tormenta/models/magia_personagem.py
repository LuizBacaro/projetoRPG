"""Magias Tormenta 20 — vínculo personagem ↔ slug do catálogo MB (`magias_mb_catalogo.json`)."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class TormentaMagiaPersonagem(Base):
    """Magia na ficha (grimório, conhecidas ou preparadas)."""

    __tablename__ = "tormenta_magias_personagem"
    __table_args__ = (
        UniqueConstraint(
            "personagem_id",
            "magia_slug",
            "papel",
            name="uq_tormenta_magia_personagem_par",
        ),
        CheckConstraint(
            "papel IN ('grimorio', 'conhecida', 'preparada')",
            name="ck_tormenta_magia_personagem_papel",
        ),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    personagem_id = Column(
        Integer,
        ForeignKey("tormenta_personagens.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    magia_slug = Column(String(80), nullable=False, index=True)
    papel = Column(String(20), nullable=False)
    notas = Column(String(500), nullable=True)
    adicionado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    personagem = relationship("TormentaPersonagem", back_populates="magias_vinculos")
