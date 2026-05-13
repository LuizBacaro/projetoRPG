"""Personagem Tormenta 20 — ficha alinhada ao Módulo Básico (planilha oficial).

Referência de paginação no model legado: págs. 304–305 — confirmar na edição em uso.
"""

from sqlalchemy import JSON, CheckConstraint, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.shared.core.database import Base


class TormentaPersonagem(Base):
    __tablename__ = "tormenta_personagens"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('jogador', 'monstro', 'npc')",
            name="ck_tormenta_personagens_tipo_valido",
        ),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    dono_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    tipo = Column(String(20), nullable=False)
    nome = Column(String(120), nullable=False)
    jogador_nome = Column(String(120), nullable=True)
    raca = Column(String(120), nullable=True)
    classe_nivel = Column(String(160), nullable=True)
    sexo = Column(String(40), nullable=True)
    idade = Column(String(80), nullable=True)
    tendencia = Column(String(80), nullable=True)
    divindade = Column(String(120), nullable=True)

    for_valor = Column(Integer, nullable=False, default=10)
    des_valor = Column(Integer, nullable=False, default=10)
    con_valor = Column(Integer, nullable=False, default=10)
    int_valor = Column(Integer, nullable=False, default=10)
    sab_valor = Column(Integer, nullable=False, default=10)
    car_valor = Column(Integer, nullable=False, default=10)

    pv_max = Column(Integer, nullable=False, default=1)
    pv_atual = Column(Integer, nullable=False, default=1)
    pa_max = Column(Integer, nullable=False, default=0)
    pa_atual = Column(Integer, nullable=False, default=0)
    ca = Column(Integer, nullable=False, default=10)
    rd = Column(String(80), nullable=False, default="")
    nivel = Column(Integer, nullable=False, default=1)
    iniciativa = Column(Integer, nullable=False, default=0)
    deslocamento = Column(String(80), nullable=False, default="")
    tamanho = Column(String(80), nullable=False, default="")

    fort_total = Column(Integer, nullable=False, default=0)
    ref_total = Column(Integer, nullable=False, default=0)
    von_total = Column(Integer, nullable=False, default=0)

    # Perícias variáveis, equipamento, magias, notas de mesa (contrato JSON estável na API).
    ficha_json = Column(JSON, nullable=False, default=dict)
    foto_url = Column(String(2048), nullable=True)

    talentos_vinculos = relationship(
        "TormentaTalentoPersonagem",
        back_populates="personagem",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    equipamentos_vinculos = relationship(
        "TormentaEquipamentoPersonagem",
        back_populates="personagem",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    consumiveis_vinculos = relationship(
        "TormentaConsumivelPersonagem",
        back_populates="personagem",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
