"""
schemas/talento.py
SRP: Schemas Pydantic para serialização de Talentos
SOLID: Single Responsibility — apenas validação/serialização
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TalentoBase(BaseModel):
    """Schema base com campos comuns"""
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    pagina_referencia: Optional[str] = Field(default=None, max_length=50)
    ativo: bool = True


class TalentoCreate(TalentoBase):
    """Schema para criação de talentos"""
    pass


class TalentoResponse(TalentoBase):
    """Schema de resposta — inclui campos gerados pelo banco"""
    id: int
    criado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class TalentoJogadorBase(BaseModel):
    """Schema base para talento do jogador"""
    talento_id: int


class TalentoJogadorCreate(TalentoJogadorBase):
    """Schema para adicionar talento ao jogador"""
    pass


class TalentoJogadorResponse(TalentoJogadorBase):
    """Schema de resposta completa"""
    id: int
    combatente_id: int
    talento: TalentoResponse
    adicionado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class TalentoJogadorListResponse(BaseModel):
    """Schema para listagem de talentos do jogador"""
    id: int
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    pagina_referencia: Optional[str] = Field(default=None, max_length=50)

    class Config:
        from_attributes = True
