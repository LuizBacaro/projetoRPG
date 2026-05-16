"""Schemas — equipamentos do personagem Tormenta."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class TormentaEquipamentoPersonagemItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    equipamento_id: int
    nome: str
    categoria: Optional[str] = None
    quantidade: int = Field(ge=1, le=9999)
    notas: Optional[str] = None
    adicionado_em: datetime


class TormentaEquipamentoVinculoCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    equipamento_id: Optional[int] = Field(None, ge=1)
    nome: Optional[str] = Field(None, max_length=200)
    quantidade: int = Field(default=1, ge=1, le=9999)
    notas: Optional[str] = Field(None, max_length=500)

    @model_validator(mode="after")
    def _xor(self) -> TormentaEquipamentoVinculoCreate:
        tid = self.equipamento_id is not None
        nom = self.nome is not None and str(self.nome).strip() != ""
        if tid == nom:
            raise ValueError("Informe exatamente um entre equipamento_id ou nome")
        return self


class TormentaEquipamentoVinculoPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    quantidade: int = Field(ge=1, le=9999)


class TormentaMigrarEquipJsonResponse(BaseModel):
    vinculos_criados: int = Field(ge=0)
    ignorados_duplicados: int = Field(ge=0)
