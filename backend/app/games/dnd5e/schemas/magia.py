"""Schemas — catálogo de magias D&D 5e."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class Dnd5eMagiaClasseItem(BaseModel):
    classe_slug: str
    nivel: int


class Dnd5eMagiaResponse(BaseModel):
    id: int
    slug: str
    nome: str
    nivel: int
    escola: Optional[str] = None
    tempo_conjuracao: Optional[str] = None
    alcance_texto: Optional[str] = None
    duracao: Optional[str] = None
    requer_concentracao: bool = False
    ritual: bool = False
    componentes: Optional[str] = None
    dano: Optional[str] = None
    teste_resistencia: Optional[str] = None
    ataque_magico: Optional[str] = None
    descricao: Optional[str] = None
    descricao_nivel_superior: Optional[str] = None
    classes: List[Dnd5eMagiaClasseItem] = Field(default_factory=list)

    class Config:
        from_attributes = True


class Dnd5eMagiaListResponse(BaseModel):
    magias: List[Dnd5eMagiaResponse]
    total: int
