"""
Modelos de Perícia para D&D 3.5
Single Responsibility: Apenas representam a estrutura das perícias
"""

from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, Float
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

from app.database import Base


class AtributoEnum(str, PyEnum):
    """Atributos disponíveis em D&D 3.5"""
    FORCA = "FOR"
    DESTREZA = "DES"
    CONSTITUICAO = "CON"
    INTELIGENCIA = "INT"
    SABEDORIA = "SAB"
    CARISMA = "CAR"


class TipoPericiaEnum(str, PyEnum):
    """Tipos de perícias"""
    COMUM = "comum"
    CONHECIMENTO = "conhecimento"
    PROFISSAO = "profissao"
    OFICIO = "oficio"
    PERFORMANCE = "performance"


class Pericia(Base):
    """
    Tabela de perícias disponíveis em D&D 3.5
    Single Responsibility: Armazenar definições de perícias
    """
    __tablename__ = "pericias"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False, index=True)
    descricao = Column(Text, nullable=True)
    atributo = Column(String(3), nullable=False)  # FOR, DES, CON, INT, SAB, CAR
    tipo = Column(String(20), default=TipoPericiaEnum.COMUM, nullable=False)
    requer_treinamento = Column(Integer, default=0)  # 1 se precisa treino
    pagina_livro = Column(Integer, nullable=True)

    # Relacionamento com perícias do jogador
    pericia_jogadores = relationship(
        "PericiaJogador",
        back_populates="pericia",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Pericia(id={self.id}, nome={self.nome}, atributo={self.atributo})>"


class PericiaJogador(Base):
    """
    Perícias do jogador com graduação e modificadores
    Single Responsibility: Armazenar dados de perícia específicas do jogador
    """
    __tablename__ = "pericia_jogadores"

    id = Column(Integer, primary_key=True, index=True)
    combatente_id = Column(Integer, ForeignKey("combatentes.id"), nullable=False)
    pericia_id = Column(Integer, ForeignKey("pericias.id"), nullable=False)
    
    graduacao = Column(Integer, default=0)  # Pontos gastos na perícia
    modificador_atributo = Column(Float, default=0)  # Modificador do atributo
    bonus_outros = Column(Float, default=0)  # Bônus de outros fatores (magias, itens, etc)
    
    # Relacionamentos
    pericia = relationship("Pericia", back_populates="pericia_jogadores")
    combatente = relationship("Combatente", back_populates="pericias")

    def __repr__(self):
        return f"<PericiaJogador(combatente_id={self.combatente_id}, pericia_id={self.pericia_id})>"

    @property
    def total_modificador(self) -> float:
        """Calcula o modificador total da perícia"""
        return self.graduacao + self.modificador_atributo + self.bonus_outros