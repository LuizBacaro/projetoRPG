"""
Schemas Pydantic de Campanha (D&D 3.5)

Localização: este módulo pertence ao pacote `app.games.dnd35.schemas`.
Existe um shim em `app.schemas.campanha` que re-exporta as classes
durante a reorganização multi-jogo.
"""

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

_HTML_TAG_RE = re.compile(r"<[^>]+>")


def _strip_html(v):
    if v is None:
        return v
    return _HTML_TAG_RE.sub("", str(v)).strip()


class CampanhaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=120)
    descricao: Optional[str] = Field(default="", max_length=500)

    @field_validator("nome", "descricao", mode="before")
    @classmethod
    def sanitizar_texto(cls, v):
        return _strip_html(v)


class CampanhaCreate(CampanhaBase):
    personagem_ids: List[int] = []


class CampanhaUpdate(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    descricao: Optional[str] = Field(default=None, max_length=500)
    personagem_ids: Optional[List[int]] = None

    @field_validator("nome", "descricao", mode="before")
    @classmethod
    def sanitizar_texto(cls, v):
        return _strip_html(v)


class CampanhaResponse(CampanhaBase):
    id: int
    mestre_id: int
    created_at: datetime
    updated_at: datetime
    total_personagens: int = 0
    personagem_ids: List[int] = []

    class Config:
        from_attributes = True
