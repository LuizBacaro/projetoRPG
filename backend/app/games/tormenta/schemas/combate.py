"""Schemas — combate Tormenta (Arena)."""

from typing import List

from pydantic import BaseModel, Field


class TormentaIniciarCombateRequest(BaseModel):
    personagem_ids: List[int] = Field(..., min_length=1)
