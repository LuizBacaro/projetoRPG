"""
schemas/magia.py
SRP: Schemas Pydantic para serialização de Magias
SOLID: Single Responsibility — apenas validação/serialização
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class MagiaBase(BaseModel):
    """Schema base com campos comuns"""
    nome:               str = Field(..., min_length=1, max_length=100)
    nivel:              int
    classe:             str = Field(..., min_length=1, max_length=50)
    escola:             Optional[str] = Field(default=None, max_length=50)
    sub_escola:         Optional[str] = Field(default=None, max_length=50)
    componentes:        Optional[str] = Field(default=None, max_length=20)
    alcance:            Optional[str] = Field(default=None, max_length=50)
    area_efeito:        Optional[str] = Field(default=None, max_length=100)
    duracao:            Optional[str] = Field(default=None, max_length=100)
    tempo_conjuracao:   Optional[str] = Field(default=None, max_length=50)
    dano:               Optional[str] = Field(default=None, max_length=50)
    teste_resistencia:  Optional[str] = Field(default=None, max_length=50)
    resistencia_magica: bool = False
    descricao:          Optional[str] = Field(default=None, max_length=1000)
    ativo:              bool = True


class MagiaResponse(MagiaBase):
    """Schema de resposta — inclui campos gerados pelo banco"""
    id:           int
    eh_truque:    bool
    tem_dano:     bool
    data_criacao: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2 (era orm_mode no v1)


class MagiaFiltro(BaseModel):
    """Schema para filtros de busca de magias"""
    classe: Optional[str] = Field(default=None, max_length=50)
    nivel:  Optional[int] = None
    escola: Optional[str] = Field(default=None, max_length=50)
    nome:   Optional[str] = Field(default=None, max_length=100)