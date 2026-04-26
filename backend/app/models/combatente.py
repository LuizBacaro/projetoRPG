"""
Model do Combatente (Entity)
SRP: representa a tabela combatentes + relacionamentos
"""
from sqlalchemy import Column, Integer, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import relationship
from ..core.database import Base
from .mixins import SoftDeleteMixin


class Combatente(SoftDeleteMixin, Base):
    __tablename__  = "combatentes"
    __table_args__ = (
        CheckConstraint("hp_atual >= -10", name="ck_combatentes_hp_atual_minimum"),
        CheckConstraint("hp_maximo > 0", name="ck_combatentes_hp_maximo_positive"),
        CheckConstraint("hp_atual <= hp_maximo", name="ck_combatentes_hp_atual_lte_hp_maximo"),
        CheckConstraint("tipo IN ('jogador', 'monstro', 'npc')", name="ck_combatentes_tipo_valido"),
        {"extend_existing": True},
    )

    # ── Identificação ──
    id     = Column(Integer, primary_key=True, index=True)
    dono_id = Column(Integer, nullable=True, index=True)
    campanha_id = Column(Integer, ForeignKey("campanhas.id"), nullable=True, index=True)
    nome   = Column(String,  nullable=False)
    tipo   = Column(String,  nullable=False)
    classe = Column(String,  nullable=False)
    raca   = Column(String,  nullable=True, default="")
    raca_slug = Column(String, nullable=True, default="")
    idiomas_customizados = Column(String, nullable=True, default="")
    divindade = Column(String, nullable=True, default="")
    alinhamento = Column(String, nullable=True, default="")
    dominios = Column(String, nullable=True, default="")

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

    # ── Economia (moedas) ──
    pc = Column(Integer, default=0)  # peça de cobre
    pp = Column(Integer, default=0)  # peça de prata
    po = Column(Integer, default=0)  # peça de ouro
    pl = Column(Integer, default=0)  # peça de platina

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
    fortitude_base = Column(Integer, default=0)
    reflexos_base  = Column(Integer, default=0)
    vontade_base   = Column(Integer, default=0)
    fortitude = Column(Integer, default=0)
    reflexos  = Column(Integer, default=0)
    vontade   = Column(Integer, default=0)

    # ── Progressão ──
    nivel  = Column(Integer, default=1)
    pontos = Column(Integer, default=0)
    bonus_base_ataque = Column(String, nullable=True, default="")
    habilidades_especiais = Column(String, nullable=True, default="")

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
    equipamentos = relationship(
        "EquipamentoJogador",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="EquipamentoJogador.combatente_id"
    )
    armaduras_protecao = relationship(
        "ArmaduraProtecaoJogador",
        cascade="all, delete-orphan",
        lazy="selectin",
        foreign_keys="ArmaduraProtecaoJogador.combatente_id",
    )
    campanha = relationship("Campanha", back_populates="personagens", lazy="joined")

    # ── Helpers de domínio ──
    def __repr__(self) -> str:
        return f"<Combatente(id={self.id}, nome='{self.nome}', tipo='{self.tipo}')>"

    def esta_vivo(self) -> bool:
        """Monstros morrem a 0 HP; Jogadores e NPCs morrem a -10 HP (D&D 3.5)."""
        if self.tipo == 'monstro':
            return self.hp_atual > 0
        return self.hp_atual > -10

    def esta_critico(self) -> bool: return 0 < self.hp_atual < self.hp_maximo * 0.25

    def aplicar_dano(self, dano: int) -> int:
        """Aplica dano. Monstros não ficam negativos; jogadores/NPCs chegam até -10."""
        if self.tipo == 'monstro':
            self.hp_atual = max(0, self.hp_atual - dano)
        else:
            self.hp_atual = max(-10, self.hp_atual - dano)
        return self.hp_atual

    def curar(self, cura: int) -> int:
        self.hp_atual = min(self.hp_maximo, self.hp_atual + cura)
        return self.hp_atual

    def resetar_hp(self) -> None:
        self.hp_atual = self.hp_maximo

    def calcular_modificador(self, atributo: str) -> int:
        return (getattr(self, atributo.lower(), 10) - 10) // 2