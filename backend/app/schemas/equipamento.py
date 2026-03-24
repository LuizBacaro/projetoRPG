"""
schemas/equipamento.py
SRP: Schemas Pydantic para serialização de Equipamentos
SOLID: Single Responsibility — apenas validação/serialização
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class EquipamentoBase(BaseModel):
    """Schema base com campos comuns"""
    nome: str
    descricao: Optional[str] = None
    pagina_referencia: Optional[str] = None
    ativo: bool = True


class EquipamentoCreate(EquipamentoBase):
    """Schema para criação de equipamentos"""
    pass


class EquipamentoResponse(EquipamentoBase):
    """Schema de resposta — inclui campos gerados pelo banco"""
    id: int
    criado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class EquipamentoJogadorBase(BaseModel):
    """Schema base para equipamento do jogador"""
    equipamento_id: int
    quantidade: int = 1


class EquipamentoJogadorCreate(EquipamentoJogadorBase):
    """Schema para adicionar equipamento ao jogador"""
    pass


class EquipamentoJogadorResponse(EquipamentoJogadorBase):
    """Schema de resposta completa"""
    id: int
    combatente_id: int
    equipamento: EquipamentoResponse
    adicionado_em: Optional[datetime] = None

    class Config:
        from_attributes = True


class EquipamentoJogadorListResponse(BaseModel):
    """Schema para listagem de equipamentos do jogador"""
    id: int
    nome: str
    descricao: Optional[str] = None
    pagina_referencia: Optional[str] = None
    quantidade: int

    class Config:
        from_attributes = True
