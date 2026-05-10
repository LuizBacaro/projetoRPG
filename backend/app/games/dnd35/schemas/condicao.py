"""
Schemas de Condição
Princípio SOLID: DIP - Define contrato de dados
"""

from typing import List, Optional

from pydantic import BaseModel, Field


class CondicaoResponse(BaseModel):
    """Schema para resposta de catálogo de condições"""

    id: int
    nome: str
    efeito: str

    class Config:
        from_attributes = True


class AplicarCondicaoRequest(BaseModel):
    """
    ✅ Schema para aplicar condição com duração opcional
    """

    condicao_id: int
    duracao_turnos: Optional[int] = -1  # ✅ NOVO: default permanente (-1)


class AplicarCondicaoMassaRequest(BaseModel):
    combatente_ids: List[int] = Field(..., min_length=1)
    condicao_id: int
    duracao_turnos: int = -1


class AplicarCondicaoMassaResponse(BaseModel):
    combatente_ids: List[int]
    total_aplicados: int
    condicao_id: int
    duracao_turnos: int


class RemoverCondicaoRequest(BaseModel):
    """Schema para remover condição"""

    condicao_id: int


class CondicaoAtivaResponse(BaseModel):
    """
    ✅ Schema para condições ativas de um combatente
    Inclui duracao_turnos
    """

    combatente_id: int
    condicoes: List[dict]  # Inclui {id, condicao_id, nome, efeito, duracao_turnos}

    class Config:
        from_attributes = True
