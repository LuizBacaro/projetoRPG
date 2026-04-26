"""Schemas de Perícia (D&D 3.5) — canônico em `app.games.dnd35.schemas.pericia`."""

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class AtributoEnum(str, Enum):
    FORCA = "FOR"
    DESTREZA = "DES"
    CONSTITUICAO = "CON"
    INTELIGENCIA = "INT"
    SABEDORIA = "SAB"
    CARISMA = "CAR"


class TipoPericiaEnum(str, Enum):
    COMUM = "comum"
    CONHECIMENTO = "conhecimento"
    PROFISSAO = "profissao"
    OFICIO = "oficio"
    PERFORMANCE = "performance"


class PericiaBase(BaseModel):
    """Schema base de perícia"""

    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    atributo: AtributoEnum
    tipo: TipoPericiaEnum = TipoPericiaEnum.COMUM
    requer_treinamento: int = Field(default=0, ge=0, le=1)
    especialidade: Optional[str] = Field(default=None, max_length=100)
    pode_usar_sem_treinamento: int = Field(default=1, ge=0, le=1)
    sofre_penalidade_armadura: int = Field(default=0, ge=0, le=1)
    pagina_livro: Optional[int] = None

    @field_validator("atributo", mode="before")
    @classmethod
    def normalizar_atributo(cls, v):
        if isinstance(v, str):
            return v.upper()
        return v


class PericiaCreate(PericiaBase):
    """Schema para criação de perícia"""

    pass


class PericiaUpdate(BaseModel):
    """Schema para atualização de perícia"""

    nome: Optional[str] = Field(default=None, min_length=1, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    atributo: Optional[AtributoEnum] = None
    tipo: Optional[TipoPericiaEnum] = None
    requer_treinamento: Optional[int] = None
    especialidade: Optional[str] = Field(default=None, max_length=100)
    pode_usar_sem_treinamento: Optional[int] = None
    sofre_penalidade_armadura: Optional[int] = None
    pagina_livro: Optional[int] = None


class PericiaResponse(PericiaBase):
    """Schema de resposta de perícia"""

    id: int
    custo_para_classe: Optional[int] = None

    class Config:
        from_attributes = True


class PericiaClasseResponse(BaseModel):
    """Schema de resposta de associação classe-perícia"""

    pericia_id: int
    classe_nome: str
    is_default: int

    class Config:
        from_attributes = True


class PericiaJogadorBase(BaseModel):
    """Schema base de perícia do jogador"""

    pericia_id: int
    graduacao: int = Field(default=0, ge=0)
    custo_total: int = Field(default=0, ge=0)
    bonus_outros: float = Field(default=0)


class PericiaJogadorCreate(PericiaJogadorBase):
    """Schema para criar perícia do jogador"""

    pass


class PericiaJogadorUpdate(BaseModel):
    """Schema para atualizar perícia do jogador"""

    graduacao: Optional[int] = Field(None, ge=0)
    custo_total: Optional[int] = Field(None, ge=0)
    bonus_outros: Optional[float] = None


class PericiaJogadorResponse(PericiaJogadorBase):
    """Schema de resposta de perícia do jogador"""

    id: int
    combatente_id: int
    modificador_atributo: float
    pericia: PericiaResponse

    @property
    def total_modificador(self) -> float:
        """Calcula o modificador total"""
        return self.graduacao + self.modificador_atributo + self.bonus_outros

    class Config:
        from_attributes = True


class PericiaJogadorListResponse(BaseModel):
    """Schema para lista de perícias do jogador"""

    pericias: List[PericiaJogadorResponse]
    total_pontos_gastos: int
    pontos_disponiveis: int
