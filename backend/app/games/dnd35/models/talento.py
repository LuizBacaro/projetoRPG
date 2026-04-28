"""Model ORM de Talentos (D&D 3.5) — canônico em `app.games.dnd35.models.talento`."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.shared.core.database import Base
from app.shared.core.mixins import SoftDeleteMixin


class Talento(SoftDeleteMixin, Base):
    """
    Modelo SQLAlchemy para representar um Talento do D&D 3.5.

    Colunas baseadas no sistema de talentos do PHB 3.5.
    SRP: mapeamento da tabela 'talentos'.
    """

    __tablename__ = "talentos"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)

    nome = Column(String(100), nullable=False, index=True)
    descricao = Column(String(1000), nullable=True)
    pagina_referencia = Column(String(50), nullable=True)
    prerequisitos = Column(String(500), nullable=True)
    secao = Column(String(200), nullable=True)

    criado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    ativo = Column(Boolean, default=True, index=True)

    combatentes = relationship(
        "TalentoJogador",
        back_populates="talento",
        cascade="all, delete-orphan",
        lazy="selectin",
    )


class TalentoJogador(Base):
    """Relacionamento N:N entre Combatente e Talento."""

    __tablename__ = "talentos_jogador"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)

    combatente_id = Column(
        Integer,
        ForeignKey("combatentes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    talento_id = Column(
        Integer,
        ForeignKey("talentos.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    adicionado_em = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    talento = relationship(
        "Talento", back_populates="combatentes", lazy="joined"
    )
