"""Schemas — combate GURPS (Arena)."""

from typing import List, Optional

from pydantic import BaseModel, Field


class GurpsIniciarCombateRequest(BaseModel):
    personagem_ids: List[int] = Field(..., min_length=1)
