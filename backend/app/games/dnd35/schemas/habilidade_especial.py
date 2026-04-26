"""
Schemas Pydantic de Habilidade Especial (D&D 3.5).

Referência PHB 3.5; canônico em `app.games.dnd35.schemas.habilidade_especial`.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HabilidadeEspecialResumo(BaseModel):
    slug: str
    titulo: str


class HabilidadeEspecialDetalhe(HabilidadeEspecialResumo):
    descricao: str = ""
    aliases: list[str] = Field(default_factory=list)
