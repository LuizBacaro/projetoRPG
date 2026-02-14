"""
Schemas Pydantic para Combate (DTOs)
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from .combatente import CombatenteResponse


class IniciarCombateRequest(BaseModel):
    """Schema para iniciar combate"""
    combatente_ids: List[int] = Field(..., min_length=1)


class CombateResponse(BaseModel):
    """Schema de resposta para Combate"""
    id: int
    combatentes_ids: List[int]
    turno_atual: int
    ativo: bool
    combatente_ativo_id: Optional[int] = None
    combatentes: Optional[List[CombatenteResponse]] = None

    class Config:
        from_attributes = True


class AplicarDanoRequest(BaseModel):
    """Schema para aplicar dano durante combate"""
    combatente_id: int = Field(..., gt=0)
    dano: int = Field(..., gt=0)