"""
schemas/equipamento.py
SRP: Schemas Pydantic para serialização de Equipamentos
SOLID: Single Responsibility — apenas validação/serialização
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class EquipamentoBase(BaseModel):
    """Schema base com campos comuns"""
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    pagina_referencia: Optional[str] = Field(default=None, max_length=50)
    
    # Novos campos da Tabela 7-5
    categoria: Optional[str] = Field(default=None, max_length=50)
    subcategoria: Optional[str] = Field(default=None, max_length=100)
    custo: Optional[str] = Field(default=None, max_length=50)
    dano_pequeno: Optional[str] = Field(default=None, max_length=20)
    dano_medio: Optional[str] = Field(default=None, max_length=20)
    critico: Optional[str] = Field(default=None, max_length=20)
    alcance_incremento: Optional[str] = Field(default=None, max_length=50)
    peso: Optional[str] = Field(default=None, max_length=20)
    tipo_dano: Optional[str] = Field(default=None, max_length=50)
    
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
    quantidade: int = Field(default=1, ge=1, le=999)


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
    nome: str = Field(..., max_length=100)
    descricao: Optional[str] = Field(default=None, max_length=500)
    pagina_referencia: Optional[str] = Field(default=None, max_length=50)
    quantidade: int

    class Config:
        from_attributes = True
