"""
Model de Divindade Custom (D&D 3.5)
SRP: Entidade que representa uma divindade criada pelo Mestre para a campanha,
somando-se ao catalogo oficial D&D 3.5 (Tabela 3-7).

Observacoes:
  * `dominios` e armazenado em CSV ("Bem, Protecao, Guerra") por simplicidade
    e compatibilidade com o restante do projeto. O service normaliza/expoe
    como List[str].
  * `nome` deve ser unico (case-insensitive) dentro das customizadas.

Divindades de campanha D&D 3.5; canônico em `app.games.dnd35.models.divindade_custom`.
"""
from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

# Declarative Base única do processo (`app.shared.core.database`) — hub e jogos partilham a mesma MetaData.
from ....shared.core.database import Base


class DivindadeCustom(Base):
    """Divindade customizada de campanha, criada por um Mestre/Administrador."""

    __tablename__ = "divindades_custom"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), nullable=False, unique=True, index=True)
    titulo = Column(String(200), nullable=False, default="")
    tendencia = Column(String(50), nullable=False)
    dominios = Column(Text, nullable=False, default="")
    descricao = Column(Text, nullable=True)

    criado_por_id = Column(
        Integer,
        ForeignKey("usuarios.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    criado_em = Column(DateTime, nullable=False, default=datetime.utcnow)

    criado_por = relationship("Usuario", foreign_keys=[criado_por_id])

    def __repr__(self) -> str:  # pragma: no cover - representacao
        return f"<DivindadeCustom(id={self.id}, nome='{self.nome}')>"
