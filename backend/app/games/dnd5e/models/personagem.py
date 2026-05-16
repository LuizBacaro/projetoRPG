"""Personagem D&D 5e — ficha persistida (RF 01 + extensível via ficha_json)."""

from sqlalchemy import JSON, CheckConstraint, Column, ForeignKey, Integer, String

from app.shared.core.database import Base


class Dnd5ePersonagem(Base):
    __tablename__ = "dnd5e_personagens"
    __table_args__ = (
        CheckConstraint(
            "tipo IN ('jogador', 'monstro', 'npc')",
            name="ck_dnd5e_personagens_tipo_valido",
        ),
        CheckConstraint("nivel >= 1 AND nivel <= 20", name="ck_dnd5e_personagens_nivel"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    dono_id = Column(Integer, ForeignKey("usuarios.id"), nullable=True, index=True)
    tipo = Column(String(20), nullable=False)
    nome = Column(String(120), nullable=False)
    jogador_nome = Column(String(120), nullable=True)
    foto_url = Column(String(2048), nullable=True)
    nivel = Column(Integer, nullable=False, default=1)
    experiencia = Column(Integer, nullable=False, default=0)

    strength = Column(Integer, nullable=False, default=10)
    dexterity = Column(Integer, nullable=False, default=10)
    constitution = Column(Integer, nullable=False, default=10)
    intelligence = Column(Integer, nullable=False, default=10)
    wisdom = Column(Integer, nullable=False, default=10)
    charisma = Column(Integer, nullable=False, default=10)

    hp_max = Column(Integer, nullable=False, default=0)
    hp_atual = Column(Integer, nullable=False, default=0)

    # Raça, classe, magias, equipamento, antecedente — contrato evolutivo na API.
    ficha_json = Column(JSON, nullable=False, default=lambda: {})
