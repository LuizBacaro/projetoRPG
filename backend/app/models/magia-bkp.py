"""
magia.py
SRP: Modelo ORM para Magias D&D 3.5 (PHB)
SOLID: Single Responsibility — apenas mapeamento de tabela de magias
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
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
    nivel             = Column(Integer,     nullable=False, index=True)   # 0–9
    classe            = Column(String(50),  nullable=False, index=True)   # Mago, Clérigo, etc.

    # ── Escola ──
    escola            = Column(String(50),  nullable=True)
    sub_escola        = Column(String(50),  nullable=True)

    # ── Mecânicas ──
    componentes       = Column(String(20),  nullable=True)   # V, S, M, F, DF
    alcance           = Column(String(50),  nullable=True)
    area_efeito       = Column(String(100), nullable=True)
    duracao           = Column(String(100), nullable=True)
    tempo_conjuracao  = Column(String(50),  nullable=True)

    # ── Combate ──
    dano              = Column(String(50),  nullable=True)
    teste_resistencia = Column(String(50),  nullable=True)   # Fortitude/Reflexos/Vontade/Nenhum
    resistencia_magica= Column(Boolean,     default=False)

    # ── Descrição ──
    descricao         = Column(String(1000), nullable=True)

    # ── Metadados ──
    ativo             = Column(Boolean,  default=True)
    data_criacao      = Column(DateTime, default=datetime.utcnow)

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
            'nivel':               self.nivel,
            'classe':              self.classe,
            'escola':              self.escola,
            'sub_escola':          self.sub_escola,
            'componentes':         self.componentes,
            'alcance':             self.alcance,
            'area_efeito':         self.area_efeito,
            'duracao':             self.duracao,
            'tempo_conjuracao':    self.tempo_conjuracao,
            'dano':                self.dano,
            'teste_resistencia':   self.teste_resistencia,
            'resistencia_magica':  self.resistencia_magica,
            'descricao':           self.descricao,
            'ativo':               self.ativo,
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