"""
Model do Combatente (Entity)
SRP: representa a tabela combatentes + relacionamentos
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from ..core.database import Base


class Combatente(Base):
    __tablename__  = "combatentes"
    __table_args__ = {"extend_existing": True}

    # ── Identificação ──
    id     = Column(Integer, primary_key=True, index=True)
    nome   = Column(String,  nullable=False)
    tipo   = Column(String,  nullable=False)
    classe = Column(String,  nullable=False)
    raca   = Column(String,  nullable=True, default="")

    # ── Referência (apenas monstros) ──
    pagina_referencia = Column(String, nullable=True, default="")  # ✅ NOVO

    # ── Combate ──
    hp_atual   = Column(Integer, nullable=False)
    hp_maximo  = Column(Integer, nullable=False)
    iniciativa = Column(Integer, nullable=False, default=0)

    # ── Defesa ──
    ca       = Column(Integer, default=10)
    toque    = Column(Integer, default=10)
    surpresa = Column(Integer, default=10)

    # ── Visual ──
    foto_url = Column(String, nullable=True)

    # ── Atributos D&D ──
    forca        = Column(Integer, default=10)
    destreza     = Column(Integer, default=10)
    constituicao = Column(Integer, default=10)
    inteligencia = Column(Integer, default=10)
    sabedoria    = Column(Integer, default=10)
    carisma      = Column(Integer, default=10)

    # ── Resistências ──
    fortitude = Column(Integer, default=0)
    reflexos  = Column(Integer, default=0)
    vontade   = Column(Integer, default=0)

    # ── Progressão ──
    nivel  = Column(Integer, default=1)
    pontos = Column(Integer, default=0)

    # ── Relacionamentos ──
    ataques = relationship(
        "Ataque",
        back_populates="combatente",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    magias_slots = relationship(
        "MagiaSlot",
        back_populates="combatente",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="MagiaSlot.nivel",
    )
    pericias = relationship(
        "PericiaJogador",
        back_populates="combatente",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    magias_preparadas = relationship(
        "MagiaPreparada",
        back_populates="combatente",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="MagiaPreparada.nivel_slot",
    )

    # ── Helpers de domínio ──
    def __repr__(self) -> str:
        return f"<Combatente(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"

    def esta_vivo(self)    -> bool: return self.hp_atual > 0
    def esta_critico(self) -> bool: return self.hp_atual < self.hp_maximo * 0.25

    def aplicar_dano(self, dano: int) -> int:
        self.hp_atual = max(0, self.hp_atual - dano)
        return self.hp_atual

    def curar(self, cura: int) -> int:
        self.hp_atual = min(self.hp_maximo, self.hp_atual + cura)
        return self.hp_atual

    def resetar_hp(self) -> None:
        self.hp_atual = self.hp_maximo

    def calcular_modificador(self, atributo: str) -> int:
        return (getattr(self, atributo.lower(), 10) - 10) // 2