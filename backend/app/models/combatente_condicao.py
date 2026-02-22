"""
Model pivot: CombatenteCondicao
Relacionamento N:N entre Combatente e Condição sem ORM relationship
para manter consistência com a arquitetura existente.
"""
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from ..core.database import Base


class CombatenteCondicao(Base):
    """
    Tabela pivot que associa um combatente a uma condição ativa.
    Remoção manual — sem controle de duração por turnos.
    """
    __tablename__ = "combatente_condicoes"
    __table_args__ = (
        UniqueConstraint("combatente_id", "condicao_id", name="uq_combatente_condicao"),
        {'extend_existing': True}
    )

    id             = Column(Integer, primary_key=True, index=True)
    combatente_id  = Column(Integer, ForeignKey("combatentes.id", ondelete="CASCADE"), nullable=False)
    condicao_id    = Column(Integer, ForeignKey("condicoes.id",    ondelete="CASCADE"), nullable=False)