"""Sessão de combate Tormenta 20 na Arena (ordem por iniciativa, um ativo por utilizador)."""

from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer

from app.shared.core.database import Base


class TormentaCombate(Base):
    __tablename__ = "tormenta_combates"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False, index=True)
    personagens_ids = Column(JSON, nullable=False)
    turno_atual = Column(Integer, default=0)
    rodada_atual = Column(Integer, default=1)
    ativo = Column(Boolean, default=True)

    def obter_personagem_ativo_id(self):
        if not self.personagens_ids or self.turno_atual >= len(self.personagens_ids):
            return None
        return self.personagens_ids[self.turno_atual]

    def avancar_turno(self) -> int:
        if not self.personagens_ids:
            return 0
        self.turno_atual = (self.turno_atual + 1) % len(self.personagens_ids)
        if self.turno_atual == 0:
            self.rodada_atual += 1
        return self.turno_atual

    def finalizar(self) -> None:
        self.ativo = False
