"""
magia.py
SRP: Modelo ORM para Magias D&D 3.5 (PHB)
SOLID: Single Responsibility — apenas mapeamento de tabela de magias
"""

from sqlalchemy import JSON, Column, Integer, String, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from ..core.database import Base 


class Magia(Base):
    """
    Modelo SQLAlchemy para representar uma Magia do D&D 3.5 (PHB).

    Colunas baseadas na planilha oficial D&D 3.5 Geral.
    SRP: Única responsabilidade — mapeamento da tabela 'magias'.
    """

    __tablename__ = 'magias'
    __table_args__ = {'extend_existing': True}

    # ── Primary Key ──
    id = Column(Integer, primary_key=True, index=True)

    # ── Identificação ──
    nome              = Column(String(100), nullable=False, index=True)
    nome_en           = Column(String(100), nullable=True)
    nivel             = Column(Integer,     nullable=False, index=True)   # 0–9
    classe            = Column(String(50),  nullable=False, index=True)   # Mago, Clérigo, etc.

    # ── Escola ──
    escola            = Column(String(50),  nullable=True)
    sub_escola        = Column(String(50),  nullable=True)
    descritor         = Column(String(200), nullable=True)

    # ── Mecânicas ──
    componentes       = Column(String(20),  nullable=True)   # V, S, M, F, DF
    componente_extra  = Column(String(300), nullable=True)
    alcance           = Column(String(50),  nullable=True)
    area_efeito       = Column(String(100), nullable=True)
    duracao           = Column(String(100), nullable=True)
    tempo_conjuracao  = Column(String(50),  nullable=True)

    # ── Combate ──
    dano              = Column(String(50),  nullable=True)
    teste_resistencia = Column(String(50),  nullable=True)   # Fortitude/Reflexos/Vontade/Nenhum
    resistencia_magica= Column(Boolean,     default=False)
    resistencia_magia_texto = Column(String(50), nullable=True)

    # ── Descrição ──
    descricao         = Column(String(1000), nullable=True)
    descricao_en      = Column(String(1000), nullable=True)

    # ── Metadados ──
    ativo             = Column(Boolean,  default=True)
    e_magia_dominio   = Column(Boolean, default=False)
    dominios          = Column(String(250), nullable=True)
    pagina_referencia = Column(Integer, nullable=True)
    data_criacao      = Column(DateTime, default=datetime.utcnow)

    classes_niveis = relationship(
        "MagiaClasse",
        back_populates="magia",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # ── Properties ──

    @property
    def eh_truque(self) -> bool:
        """True se for truque/cantrip (nível 0)"""
        return self.nivel == 0

    @property
    def tem_dano(self) -> bool:
        """True se a magia causa dano"""
        return bool(self.dano and self.dano.strip())

    # ── Métodos Helper ──

    def para_dict(self) -> dict:
        """Converte para dicionário — útil para serialização FastAPI"""
        return {
            'id':                  self.id,
            'nome':                self.nome,
            'nome_en':             self.nome_en,
            'nivel':               self.nivel,
            'classe':              self.classe,
            'escola':              self.escola,
            'sub_escola':          self.sub_escola,
            'descritor':           self.descritor,
            'componentes':         self.componentes,
            'componente_extra':    self.componente_extra,
            'alcance':             self.alcance,
            'area_efeito':         self.area_efeito,
            'duracao':             self.duracao,
            'tempo_conjuracao':    self.tempo_conjuracao,
            'dano':                self.dano,
            'teste_resistencia':   self.teste_resistencia,
            'resistencia_magica':  self.resistencia_magica,
            'resistencia_magia_texto': self.resistencia_magia_texto,
            'descricao':           self.descricao,
            'descricao_en':        self.descricao_en,
            'ativo':               self.ativo,
            'e_magia_dominio':     self.e_magia_dominio,
            'dominios':            self.dominios,
            'pagina_referencia':   self.pagina_referencia,
            'eh_truque':           self.eh_truque,
            'tem_dano':            self.tem_dano,
            'data_criacao':        self.data_criacao.isoformat() if self.data_criacao else None,
        }

    def __repr__(self):
        return (
            f'<Magia('
            f'id={self.id}, '
            f'nome={self.nome!r}, '
            f'nivel={self.nivel}, '
            f'classe={self.classe!r}'
            f')>'
        )


class MagiaClasse(Base):
    """Relação N:N simplificada para mapear níveis por classe de uma magia."""

    __tablename__ = "magias_classes"
    __table_args__ = (
        UniqueConstraint("magia_id", "classe", name="uq_magias_classes_magia_classe"),
        {"extend_existing": True},
    )

    id = Column(Integer, primary_key=True, index=True)
    magia_id = Column(Integer, ForeignKey("magias.id", ondelete="CASCADE"), nullable=False, index=True)
    classe = Column(String(50), nullable=False, index=True)
    nivel = Column(Integer, nullable=False)

    magia = relationship("Magia", back_populates="classes_niveis")


class MagiaHistorico(Base):
    """Historico de alteracoes aplicadas no catalogo de magias."""

    __tablename__ = "magia_historico"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    magia_id = Column(Integer, nullable=True, index=True)
    usuario_id = Column(Integer, nullable=True, index=True)
    acao = Column(String(20), nullable=False)
    dados_anteriores = Column(JSON, nullable=True)
    dados_novos = Column(JSON, nullable=True)
    criado_em = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)