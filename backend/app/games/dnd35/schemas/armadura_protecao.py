"""
schemas/armadura_protecao.py
SRP: validação/serialização de armadura/item de proteção
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ArmaduraProtecaoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=120)
    tipo: str = Field(..., min_length=1, max_length=60)
    bonus_ca: int = Field(default=0, ge=-20, le=30)
    des_max: Optional[str] = Field(default=None, max_length=20)
    penalidade: int = Field(default=0, ge=-20, le=20)
    falha_arcana: Optional[str] = Field(default=None, max_length=20)
    deslocamento: Optional[str] = Field(default=None, max_length=40)
    peso: Optional[float] = Field(default=None, ge=0, le=2000)
    propriedades_especiais: Optional[str] = Field(default=None, max_length=600)
    ativo: bool = True


class ArmaduraProtecaoCreate(ArmaduraProtecaoBase):
    pass


class ArmaduraProtecaoResponse(ArmaduraProtecaoBase):
    id: int
    criado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class ArmaduraProtecaoJogadorCreate(BaseModel):
    item_id: int


class ArmaduraProtecaoJogadorListResponse(BaseModel):
    id: int
    nome: str
    tipo: str
    bonus_ca: int
    des_max: Optional[str] = None
    penalidade: int
    falha_arcana: Optional[str] = None
    deslocamento: Optional[str] = None
    peso: Optional[float] = None
    propriedades_especiais: Optional[str] = None

    class Config:
        from_attributes = True


class BonusCaResponse(BaseModel):
    bonus_ca_total: int
