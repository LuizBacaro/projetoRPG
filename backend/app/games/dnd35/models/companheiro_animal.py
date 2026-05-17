from datetime import datetime, timezone

from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class CompanheiroAnimal(Base):
    """Instância de companheiro animal (1:1 com combatente jogador)."""

    __tablename__ = "companheiros_animais"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    especie_slug = Column(String(60), nullable=False, index=True)
    nome = Column(String(120), nullable=False)
    forca = Column(Integer, nullable=False, default=10)
    destreza = Column(Integer, nullable=False, default=10)
    constituicao = Column(Integer, nullable=False, default=10)
    inteligencia = Column(Integer, nullable=False, default=10)
    sabedoria = Column(Integer, nullable=False, default=10)
    carisma = Column(Integer, nullable=False, default=10)
    bonus_atributos = Column(JSON, nullable=False, default=dict)
    hp_atual = Column(Integer, nullable=False, default=1)
    hp_maximo = Column(Integer, nullable=False, default=1)
    ca = Column(Integer, nullable=False, default=10)
    iniciativa = Column(Integer, nullable=True)
    deslocamento = Column(String(80), nullable=True)
    truques = Column(JSON, nullable=False, default=list)
    talentos = Column(JSON, nullable=False, default=list)
    pericias = Column(JSON, nullable=False, default=list)
    ataques = Column(JSON, nullable=False, default=list)
    anotacoes = Column(Text, nullable=True)
    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    atualizado_em = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    combatente = relationship(
        "Combatente",
        back_populates="companheiro_animal",
        lazy="joined",
    )
