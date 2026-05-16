"""Resposta da importação única de inventário legado (ficha_json → SQL)."""

from pydantic import BaseModel, Field


class TormentaInventarioLegadoImportResponse(BaseModel):
    talentos_criados: int = Field(ge=0)
    talentos_duplicados: int = Field(ge=0)
    equipamentos_criados: int = Field(ge=0)
    equipamentos_duplicados: int = Field(ge=0)
    consumiveis_criados: int = Field(ge=0)
    consumiveis_duplicados: int = Field(ge=0)
