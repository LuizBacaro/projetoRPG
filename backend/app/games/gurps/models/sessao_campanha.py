"""Sessão de campanha GURPS — resumo por mesa e visibilidade para jogadores."""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, false
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.shared.core.database import Base


class GurpsSessaoCampanha(Base):
    __tablename__ = "gurps_campanhas_sessoes"

    id = Column(Integer, primary_key=True, index=True)
    campanha_id = Column(
        Integer,
        ForeignKey("gurps_campanhas.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    resumo = Column(String(4000), nullable=False)
    visivel_jogadores = Column(
        Boolean, nullable=False, default=False, server_default=false()
    )
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    campanha = relationship(
        "GurpsCampanha", back_populates="sessoes", lazy="joined"
    )
