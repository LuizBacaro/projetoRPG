"""
Model do Combate (Entity)
"""
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String

from app.shared.core.database import Base


class Combate(Base):
    """
    Entidade que representa um combate ativo
    """
    __tablename__ = "combates"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    combatentes_ids = Column(JSON, nullable=False)
    turno_atual = Column(Integer, default=0)
    rodada_atual = Column(Integer, default=1)  # ← NOVO: contador de rodadas
    ativo = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Combate(id={self.id}, ativo={self.ativo}, rodada={self.rodada_atual}, turno={self.turno_atual})>"

    def obter_combatente_ativo_id(self) -> int:
        """Retorna o ID do combatente cujo turno está ativo"""
        if not self.combatentes_ids or self.turno_atual >= len(self.combatentes_ids):
            return None
        return self.combatentes_ids[self.turno_atual]

    def avancar_turno(self) -> int:
        """
        Avança para o próximo turno
        Se completar uma rodada (todos jogaram), incrementa rodada
        Retorna o índice do novo turno
        """
        if not self.combatentes_ids:
            return 0

        self.turno_atual = (self.turno_atual + 1) % len(self.combatentes_ids)

        # Se voltou ao início, completou uma rodada
        if self.turno_atual == 0:
            self.rodada_atual += 1

        return self.turno_atual

    def finalizar(self) -> None:
        """Finaliza o combate"""
        self.ativo = False

    def obter_total_combatentes(self) -> int:
        """Retorna o total de combatentes no combate"""
        return len(self.combatentes_ids) if self.combatentes_ids else 0


class CombateHistorico(Base):
    """Entidade que representa o resultado de um combate finalizado."""

    __tablename__ = "combates_historico"

    id = Column(Integer, primary_key=True, index=True)
    combate_id = Column(Integer, nullable=True, index=True)
    combatentes_ids = Column(JSON, nullable=False)

    total_combatentes = Column(Integer, nullable=False, default=0)
    total_vivos = Column(Integer, nullable=False, default=0)
    total_rodadas = Column(Integer, nullable=False, default=0)
    total_turnos = Column(Integer, nullable=False, default=0)

    vencedor_id = Column(Integer, nullable=True)
    vencedor_nome = Column(String(120), nullable=True)
    vencedor_tipo = Column(String(20), nullable=True)

    motivo_encerramento = Column(String(40), nullable=False, default="manual")
    estatisticas = Column(JSON, nullable=False, default=dict)
    finalizado_em = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc), index=True)

    def __repr__(self):
        return (
            f"<CombateHistorico(id={self.id}, combate_id={self.combate_id}, "
            f"motivo='{self.motivo_encerramento}')>"
        )
