"""
Schemas Pydantic para Condição (DTOs)
Princípio SOLID: SRP - Apenas validação/serialização de Condição
"""
from pydantic import BaseModel, Field
from typing import List


class CondicaoResponse(BaseModel):
    """Schema de resposta para Condição"""
    id:     int
    nome:   str
    efeito: str

    class Config:
        from_attributes = True


class AplicarCondicaoRequest(BaseModel):
    """Schema para aplicar condição a um combatente"""
    condicao_id: int = Field(..., gt=0)


class RemoverCondicaoRequest(BaseModel):
    """Schema para remover condição de um combatente"""
    condicao_id: int = Field(..., gt=0)


class CondicaoAtivaResponse(BaseModel):
    """Schema de resposta de condição ativa em um combatente"""
    combatente_id: int
    condicoes:     List[CondicaoResponse]