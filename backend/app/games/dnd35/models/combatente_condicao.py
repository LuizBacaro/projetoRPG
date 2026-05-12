"""
Model pivot: CombatenteCondicao
Relacionamento N:N entre Combatente e Condição COM duração em turnos.
"""

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint

from app.shared.core.database import Base


class CombatenteCondicao(Base):
    """
    Tabela pivot que associa um combatente a uma condição ativa com duração.

    Exemplos:
    - duracao_turnos = 2  → condição ativa por 2 turnos
    - duracao_turnos = -1 → condição permanente (até ser removida manualmente)
    - duracao_turnos = 0  → deve ser removida no próximo avancar_turno()
    """

    __tablename__ = "combatente_condicoes"
    __table_args__ = (
        UniqueConstraint("combatente_id", "condicao_id", name="uq_combatente_condicao"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(
        Integer, ForeignKey("combatentes.id", ondelete="CASCADE"), nullable=False
    )
    condicao_id = Column(
        Integer, ForeignKey("condicoes.id", ondelete="CASCADE"), nullable=False
    )
    # ✅ NOVO: duração em turnos (-1 = permanente, 0+ = turnos restantes)
    duracao_turnos = Column(Integer, default=-1, nullable=False)

    def __repr__(self):
        dur_txt = (
            "permanente"
            if self.duracao_turnos == -1
            else f"{self.duracao_turnos} turnos"
        )
        return f"<CombatenteCondicao(combatente_id={self.combatente_id}, condicao_id={self.condicao_id}, duracao={dur_txt})>"

    def esta_ativa(self) -> bool:
        """Verifica se a condição ainda está ativa (duração > 0 ou permanente)"""
        return self.duracao_turnos != 0

    def decrementar_duracao(self) -> bool:
        """
        Decrementa a duração em 1 turno.
        Retorna True se deve ser removida (duração = 0 após decremento)
        """
        if self.duracao_turnos > 0:
            self.duracao_turnos -= 1
            return self.duracao_turnos == 0
        return False  # Permanente ou já expirada
