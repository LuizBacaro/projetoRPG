"""
Modelos de Perícia para D&D 3.5
Single Responsibility: Apenas representam a estrutura das perícias
SOLID: Dependency Injection via Base declarativo centralizado
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from typing import TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.combatente import Combatente



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
    especialidade = Column(String(100), nullable=True)  # Para Atuação (canto), Conhecimento (Arcano), etc
    requer_treinamento = Column(Integer, default=0)  # 1 se precisa treino
    pode_usar_sem_treinamento = Column(Integer, default=1)  # 1 se pode usar sem treino
    sofre_penalidade_armadura = Column(Integer, default=0)  # 1 se sofre penalidade
    pagina_livro = Column(Integer, nullable=True)

    # ✅ Relacionamentos
    pericia_jogadores = relationship(
        "PericiaJogador",
        back_populates="pericia",
        cascade="all, delete-orphan"
    )
    
    pericias_classes = relationship(
        "PericiaClasse",
        back_populates="pericia",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Pericia(id={self.id}, nome={self.nome}, atributo={self.atributo})>"


class PericiaClasse(Base):
    """
    Associação entre Perícia e Classe D&D
    Define se uma perícia é de classe (custo 1) ou não (custo 2)
    """
    __tablename__ = "pericias_classes"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    pericia_id = Column(Integer, ForeignKey("pericias.id", ondelete="CASCADE"), nullable=False)
    classe_nome = Column(String(20), nullable=False)  # Bárbaro, Bardo, etc
    is_default = Column(Integer, default=1)  # 1 = perícia de classe, 0 = perícia fora de classe

    # ✅ Relacionamentos
    pericia = relationship("Pericia", back_populates="pericias_classes")

    def __repr__(self):
        return f"<PericiaClasse(pericia_id={self.pericia_id}, classe={self.classe_nome}, default={self.is_default})>"


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
    custo_total = Column(Integer, default=0)  # Pontos de perícia totais gastos (inclui penalidade de classe)
    modificador_atributo = Column(Float, default=0)  # Modificador do atributo
    bonus_outros = Column(Float, default=0)  # Bônus de outros fatores (magias, itens, etc)
    
    # ✅ Relacionamentos (certifique-se que back_populates existe em ambos)
    pericia = relationship("Pericia", back_populates="pericia_jogadores")
    combatente = relationship("Combatente", back_populates="pericias", lazy="select")

    def __repr__(self):
        return f"<PericiaJogador(combatente_id={self.combatente_id}, pericia_id={self.pericia_id})>"

    @property
    def total_modificador(self) -> float:
        """Calcula o modificador total da perícia"""
        return self.graduacao + self.modificador_atributo + self.bonus_outros