"""Personagem GURPS (ficha por pontos) — combatente lógico da Arena."""

from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    Column,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
)
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class GurpsPersonagem(Base):
    __tablename__ = "gurps_personagens"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('jogador', 'monstro', 'npc')",
            name="ck_gurps_personagens_tipo_valido",
        ),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    dono_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    campanha_id = Column(Integer, ForeignKey("gurps_campanhas.id"), nullable=True, index=True)
    tipo = Column(String(20), nullable=False)
    nome = Column(String(120), nullable=False)
    conceito = Column(String(200), nullable=True, default="")
    reacao = Column(String(40), nullable=True, default="")
    idade = Column(String(80), nullable=True, default="")
    foto_url = Column(String(500), nullable=True)
    # Legado / anotação na ficha; ordem de turno na arena usa velocidade_valor (VB) + DX + sorteio (G0.1).
    iniciativa = Column(Integer, nullable=False, default=0)

    st_custo = Column(Integer, nullable=False, default=0)
    st_valor = Column(Integer, nullable=False, default=10)
    dx_custo = Column(Integer, nullable=False, default=0)
    dx_valor = Column(Integer, nullable=False, default=10)
    iq_custo = Column(Integer, nullable=False, default=0)
    iq_valor = Column(Integer, nullable=False, default=10)
    ht_custo = Column(Integer, nullable=False, default=0)
    ht_valor = Column(Integer, nullable=False, default=10)
    vontade_custo = Column(Integer, nullable=False, default=0)
    vontade_valor = Column(Integer, nullable=False, default=10)
    percepcao_custo = Column(Integer, nullable=False, default=0)
    percepcao_valor = Column(Integer, nullable=False, default=10)
    pvs_custo = Column(Integer, nullable=False, default=0)
    pvs_valor = Column(Integer, nullable=False, default=10)
    pvs_atual = Column(Integer, nullable=False, default=10)
    fadiga_custo = Column(Integer, nullable=False, default=0)
    fadiga_valor = Column(Integer, nullable=False, default=10)
    fadiga_atual = Column(Integer, nullable=False, default=10)
    velocidade_custo = Column(Integer, nullable=False, default=0)
    velocidade_valor = Column(Numeric(10, 2), nullable=False, default=Decimal("5.00"))
    deslocamento_custo = Column(Integer, nullable=False, default=0)
    deslocamento_valor = Column(Integer, nullable=False, default=5)
    esquiva = Column(Integer, nullable=False, default=0)
    aparar = Column(Integer, nullable=False, default=0)
    bloqueio = Column(String(20), nullable=True)
    dano_impacto = Column(String(40), nullable=True, default="")
    dano_balanco = Column(String(40), nullable=True, default="")
    pontos_atributos = Column(Integer, nullable=False, default=0)
    pontos_vantagens = Column(Integer, nullable=False, default=0)
    pontos_desvantagens = Column(Integer, nullable=False, default=0)
    pontos_pericias = Column(Integer, nullable=False, default=0)
    pontos_total = Column(Integer, nullable=False, default=0)
    # Encargo, locais de acerto, equipamento livre, notas — JSON livre (contrato na ficha).
    extras_json = Column(JSON, nullable=False, default=dict)

    campanha = relationship("GurpsCampanha", back_populates="personagens")
    vantagens = relationship(
        "GurpsPersonagemVantagem",
        back_populates="personagem",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    desvantagens = relationship(
        "GurpsPersonagemDesvantagem",
        back_populates="personagem",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    pericias = relationship(
        "GurpsPersonagemPericia",
        back_populates="personagem",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def esta_consciente(self) -> bool:
        return (self.pvs_atual or 0) > 0


class GurpsPersonagemVantagem(Base):
    __tablename__ = "gurps_personagem_vantagens"

    id = Column(Integer, primary_key=True, index=True)
    personagem_id = Column(
        Integer, ForeignKey("gurps_personagens.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome = Column(String(500), nullable=False)
    custo = Column(Integer, nullable=False, default=0)

    personagem = relationship("GurpsPersonagem", back_populates="vantagens")


class GurpsPersonagemDesvantagem(Base):
    __tablename__ = "gurps_personagem_desvantagens"

    id = Column(Integer, primary_key=True, index=True)
    personagem_id = Column(
        Integer, ForeignKey("gurps_personagens.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome = Column(String(500), nullable=False)
    custo = Column(Integer, nullable=False, default=0)

    personagem = relationship("GurpsPersonagem", back_populates="desvantagens")


class GurpsPersonagemPericia(Base):
    __tablename__ = "gurps_personagem_pericias"

    id = Column(Integer, primary_key=True, index=True)
    personagem_id = Column(
        Integer, ForeignKey("gurps_personagens.id", ondelete="CASCADE"), nullable=False, index=True
    )
    nome = Column(String(500), nullable=False)
    tipo = Column(String(20), nullable=False)
    nh = Column(Integer, nullable=False, default=0)
    custo = Column(Integer, nullable=False, default=0)

    personagem = relationship("GurpsPersonagem", back_populates="pericias")
