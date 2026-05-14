"""Schemas — vínculos de magias MB na ficha Tormenta."""

from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


TormentaMagiaPapelMb = Literal["grimorio", "conhecida", "preparada"]


class TormentaMagiaVinculoCreate(BaseModel):
    magia_slug: str = Field(..., min_length=1, max_length=80)
    papel: TormentaMagiaPapelMb = Field(
        ...,
        description="grimorio = livro do mago; conhecida = espontâneo/lista; preparada = magias preparadas hoje.",
    )
    notas: Optional[str] = Field(None, max_length=500)


class TormentaMagiaPersonagemItem(BaseModel):
    id: int
    magia_slug: str
    papel: str
    nome: Optional[str] = Field(None, max_length=200)
    circulo: Optional[int] = Field(None, ge=0, le=20)
    tipo: Optional[str] = Field(None, max_length=20)
    escola: Optional[str] = Field(None, max_length=80)
    notas: Optional[str] = None
    adicionado_em: datetime
