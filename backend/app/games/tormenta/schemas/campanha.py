"""Schemas — campanhas Tormenta 20."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class TormentaCampanhaCreate(BaseModel):
    nome: str = Field(..., max_length=120)
    descricao: Optional[str] = Field(None, max_length=500)
    personagem_ids: Optional[List[int]] = None
    regras_opcionais_ativas: Optional[List[str]] = Field(
        None,
        description="Módulos de regras opcionais ativos na campanha (ex.: combate_avancado, lesoes).",
    )


class TormentaCampanhaUpdate(BaseModel):
    nome: Optional[str] = Field(None, max_length=120)
    descricao: Optional[str] = Field(None, max_length=500)
    personagem_ids: Optional[List[int]] = None
    regras_opcionais_ativas: Optional[List[str]] = Field(
        None,
        description="Módulos de regras opcionais ativos na campanha.",
    )


class TormentaCampanhaAssociarPersonagens(BaseModel):
    """Corpo de POST /tormenta/campanhas/{id}/personagens."""

    personagem_ids: List[int] = Field(default_factory=list)


class TormentaCampanhaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    mestre_id: int
    nome: str
    descricao: Optional[str] = ""
    regras_opcionais_ativas: Optional[List[str]] = Field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    total_personagens: int = 0
    personagem_ids: List[int] = Field(default_factory=list)
