"""Contratos para ativação de habilidades concedidas pela origem."""

from pydantic import BaseModel, ConfigDict, Field


class TormentaHabilidadeOrigemAtivarRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    habilidade_id: str = Field(..., min_length=1, max_length=60)


class TormentaHabilidadeOrigemAtivarResponse(BaseModel):
    habilidade_id: str
    nome: str
    origem_slug: str
    origem_nome: str
    custo_pm: int = Field(ge=0)
    pa_atual_antes: int
    pa_atual_depois: int
    pa_max: int
    frequencia: str = ""
    duracao: str = ""
    resumo: str = ""
