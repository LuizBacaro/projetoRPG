"""
Schemas de Perícia para validação
Single Responsibility: Apenas validam dados
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


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
    descricao: Optional[str] = None
    atributo: AtributoEnum
    tipo: TipoPericiaEnum = TipoPericiaEnum.COMUM
    requer_treinamento: int = Field(default=0, ge=0, le=1)
    pagina_livro: Optional[int] = None


class PericiaCreate(PericiaBase):
    """Schema para criação de perícia"""
    pass


class PericiaUpdate(BaseModel):
    """Schema para atualização de perícia"""
    nome: Optional[str] = None
    descricao: Optional[str] = None
    atributo: Optional[AtributoEnum] = None
    tipo: Optional[TipoPericiaEnum] = None
    requer_treinamento: Optional[int] = None
    pagina_livro: Optional[int] = None


class PericiaResponse(PericiaBase):
    """Schema de resposta de perícia"""
    id: int

    class Config:
        from_attributes = True


class PericiaJogadorBase(BaseModel):
    """Schema base de perícia do jogador"""
    pericia_id: int
    graduacao: int = Field(default=0, ge=0)
    bonus_outros: float = Field(default=0)


class PericiaJogadorCreate(PericiaJogadorBase):
    """Schema para criar perícia do jogador"""
    pass


class PericiaJogadorUpdate(BaseModel):
    """Schema para atualizar perícia do jogador"""
    graduacao: Optional[int] = Field(None, ge=0)
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