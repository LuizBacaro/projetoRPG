from __future__ import annotations

from pydantic import BaseModel, Field


class HabilidadeEspecialResumo(BaseModel):
    slug: str
    titulo: str


class HabilidadeEspecialDetalhe(HabilidadeEspecialResumo):
    descricao: str = ""
    aliases: list[str] = Field(default_factory=list)
