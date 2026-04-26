"""
Schemas Pydantic de Habilidade Especial (D&D 3.5)

Localização: este módulo pertence ao pacote `app.games.dnd35.schemas`
porque habilidades especiais são uma referência exclusiva do PHB 3.5.
Existe um shim em `app.schemas.habilidade_especial` que re-exporta as
classes durante a reorganização multi-jogo.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class HabilidadeEspecialResumo(BaseModel):
    slug: str
    titulo: str


class HabilidadeEspecialDetalhe(HabilidadeEspecialResumo):
    descricao: str = ""
    aliases: list[str] = Field(default_factory=list)
