"""Schemas — solicitações de entrada em campanha GURPS."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GurpsCampanhaDisponivelResponse(BaseModel):
    id: int
    nome: str
    mestre_nome: str = ""


class GurpsCampanhaSolicitacaoCreate(BaseModel):
    campanha_id: int = Field(..., ge=1)
    personagem_id: int = Field(..., ge=1)


class GurpsCampanhaSolicitacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campanha_id: int
    campanha_nome: str = ""
    personagem_id: int
    personagem_nome: str = ""
    solicitante_id: int
    solicitante_nome: str = ""
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    vinculado_direto: bool = False


class GurpsCampanhaSolicitacaoListaResponse(BaseModel):
    items: List[GurpsCampanhaSolicitacaoResponse] = Field(default_factory=list)
