"""
schemas/magia.py
SRP: Schemas Pydantic para serialização de Magias
SOLID: Single Responsibility — apenas validação/serialização
"""

from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class MagiaBase(BaseModel):
    """Schema base com campos comuns"""
    nome:               str
    nivel:              int
    classe:             str
    escola:             Optional[str] = None
    sub_escola:         Optional[str] = None
    componentes:        Optional[str] = None
    alcance:            Optional[str] = None
    area_efeito:        Optional[str] = None
    duracao:            Optional[str] = None
    tempo_conjuracao:   Optional[str] = None
    dano:               Optional[str] = None
    teste_resistencia:  Optional[str] = None
    resistencia_magica: bool = False
    descricao:          Optional[str] = None
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
    classe: Optional[str] = None
    nivel:  Optional[int] = None
    escola: Optional[str] = None
    nome:   Optional[str] = None