"""
Schemas Pydantic de Raça (D&D 3.5)

Localização: este módulo pertence ao pacote `app.games.dnd35.schemas`.
Existe um shim em `app.schemas.raca` que re-exporta as classes durante
a reorganização multi-jogo.
"""

from __future__ import annotations

from pydantic import BaseModel


class RacaModificadorAtributo(BaseModel):
    atributo: str
    valor: int


class RacaResumoResponse(BaseModel):
    slug: str
    nome: str
    tamanho: str | None = None
    deslocamento_metros: int | None = None
    classe_favorecida: str | None = None


class RacaDetalheResponse(RacaResumoResponse):
    modificadores_habilidade: list[RacaModificadorAtributo] = []
    idiomas_iniciais: list[str] = []
    talentos_especiais: list[str] = []
    habilidades_especiais: list[str] = []
    resistencias: list[str] = []
    modificadores_ataque: list[str] = []
    modificadores_defesa: list[str] = []
    modificadores_pericia: list[str] = []
