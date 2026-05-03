"""Schemas — campanhas GURPS."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GurpsCampanhaCreate(BaseModel):
    nome: str = Field(..., max_length=120)
    descricao: Optional[str] = Field(None, max_length=500)
    personagem_ids: Optional[List[int]] = None


class GurpsCampanhaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=120)
    descricao: Optional[str] = Field(None, max_length=500)
    personagem_ids: Optional[List[int]] = None


class GurpsCampanhaAssociarPersonagens(BaseModel):
    """Corpo de POST /campanhas/{id}/personagens — adiciona vínculos sem remover os já associados."""

    personagem_ids: List[int] = Field(default_factory=list)


class GurpsCampanhaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mestre_id: int
    nome: str
    descricao: Optional[str] = ""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    total_personagens: int = 0
    personagem_ids: List[int] = Field(default_factory=list)
