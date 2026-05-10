"""Combate ativo GURPS (ordem de iniciativa por lista de IDs)."""

from sqlalchemy import JSON, Boolean, Column, Integer

from app.shared.core.database import Base


class GurpsCombate(Base):
    __tablename__ = "gurps_combates"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    personagens_ids = Column(JSON, nullable=False)
    # Estado por personagem no combate: {"<personagem_id>": "manobra"}.
    manobras_por_personagem = Column(JSON, nullable=True, default=dict)
    # Postura por personagem: {"<personagem_id>": "em_pe|agachado|deitado"}.
    posturas_por_personagem = Column(JSON, nullable=True, default=dict)
    # Condição por personagem: {"<personagem_id>": "normal|atordoado|inconsciente|morto"}.
    condicoes_por_personagem = Column(JSON, nullable=True, default=dict)
    # Contagem de defesas na rodada: {"<personagem_id>": int}
    defesas_na_rodada = Column(JSON, nullable=True, default=dict)
    turno_atual = Column(Integer, default=0)
    rodada_atual = Column(Integer, default=1)
    ativo = Column(Boolean, default=True)

    def obter_personagem_ativo_id(self):
        if not self.personagens_ids or self.turno_atual >= len(self.personagens_ids):
            return None
        return self.personagens_ids[self.turno_atual]

    def obter_manobra_ativa(self) -> str | None:
        ativo_id = self.obter_personagem_ativo_id()
        if ativo_id is None:
            return None
        mapa = self.manobras_por_personagem or {}
        return mapa.get(str(ativo_id))

    def obter_postura_ativa(self) -> str | None:
        ativo_id = self.obter_personagem_ativo_id()
        if ativo_id is None:
            return None
        mapa = self.posturas_por_personagem or {}
        return mapa.get(str(ativo_id))

    def obter_condicao_ativa(self) -> str | None:
        ativo_id = self.obter_personagem_ativo_id()
        if ativo_id is None:
            return None
        mapa = self.condicoes_por_personagem or {}
        return mapa.get(str(ativo_id))

    def avancar_turno(self) -> int:
        if not self.personagens_ids:
            return 0
        self.turno_atual = (self.turno_atual + 1) % len(self.personagens_ids)
        if self.turno_atual == 0:
            self.rodada_atual += 1
            self.defesas_na_rodada = {}
        return self.turno_atual

    def finalizar(self) -> None:
        self.ativo = False
