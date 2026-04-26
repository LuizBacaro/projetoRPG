"""
Model de Sessão de Campanha (D&D 3.5)
SRP: representa o resumo textual de cada sessão jogada de uma campanha.

Localização: este model pertence ao pacote `app.games.dnd35.models`
porque sessões pertencem ao fluxo de campanhas D&D 3.5. Existe um shim
em `app.models.sessao_campanha` que apenas re-exporta a classe durante
a reorganização multi-jogo.
"""

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class SessaoCampanha(Base):
    __tablename__ = "campanhas_sessoes"

    id = Column(Integer, primary_key=True, index=True)
    campanha_id = Column(
        Integer, ForeignKey("campanhas.id"), nullable=False, index=True
    )
    resumo = Column(String(4000), nullable=False)
    visivel_jogadores = Column(
        Boolean, nullable=False, default=False, server_default="0"
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
        "Campanha", back_populates="sessoes", lazy="joined"
    )
