"""Schemas — combate Tormenta (Arena)."""

from typing import Dict, List

from pydantic import BaseModel, Field, field_validator


class TormentaIniciarCombateRequest(BaseModel):
    personagem_ids: List[int] = Field(..., min_length=1)


class TormentaCombateCondicaoMbItem(BaseModel):
    rotulos: List[str] = Field(default_factory=list)
    tips: List[str] = Field(default_factory=list)

    @field_validator("rotulos", "tips")
    @classmethod
    def _limitar_listas(cls, v: List[str]) -> List[str]:
        out: List[str] = []
        for x in (v or [])[:80]:
            s = str(x).strip()[:1200]
            if s:
                out.append(s)
        return out


class TormentaCombateCondicoesMbRequest(BaseModel):
    """Chaves = id do personagem (string); apenas combatentes do combate ativo."""

    por_personagem: Dict[str, TormentaCombateCondicaoMbItem] = Field(..., min_length=1)
