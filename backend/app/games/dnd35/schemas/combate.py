"""
Schemas Pydantic para Combate (DTOs)
"""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.games.dnd35.schemas.combatente import CombatenteResponse


class IniciarCombateRequest(BaseModel):
    """Schema para iniciar combate"""

    combatente_ids: List[int] = Field(..., min_length=1)
    incluir_vinculos: bool = Field(
        True,
        description="Incluir companheiro animal ou familiar dos jogadores selecionados na ordem de iniciativa",
    )


class CombateResponse(BaseModel):
    """Schema de resposta para Combate"""

    id: int
    combatentes_ids: List[int]
    turno_atual: int
    rodada_atual: int
    versao: str
    ativo: bool
    combatente_ativo_id: Optional[int] = None
    combatentes: Optional[List[CombatenteResponse]] = None

    class Config:
        from_attributes = True


class AplicarDanoRequest(BaseModel):
    """Schema para aplicar dano durante combate"""

    combatente_id: int = Field(..., gt=0)
    dano: int = Field(..., gt=0)


class CombateHistoricoResponse(BaseModel):
    """Item de histórico de combate finalizado."""

    id: int
    combate_id: Optional[int] = None
    combatentes_ids: List[int]
    total_combatentes: int
    total_vivos: int
    total_rodadas: int
    total_turnos: int
    vencedor_id: Optional[int] = None
    vencedor_nome: Optional[str] = None
    vencedor_tipo: Optional[str] = None
    motivo_encerramento: str
    estatisticas: dict
    finalizado_em: datetime

    class Config:
        from_attributes = True


class CombateHistoricoListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    itens: List[CombateHistoricoResponse]
