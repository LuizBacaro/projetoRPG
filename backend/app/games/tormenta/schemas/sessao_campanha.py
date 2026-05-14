"""Schemas — sessões de campanha Tormenta 20."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TormentaSessaoCampanhaBase(BaseModel):
    campanha_id: int = Field(..., ge=1)
    resumo: str = Field(..., min_length=1, max_length=4000)
    visivel_jogadores: bool = False

    @field_validator("resumo", mode="before")
    @classmethod
    def validar_resumo(cls, value):
        texto = str(value or "").strip()
        if not texto:
            raise ValueError("Resumo da sessao e obrigatorio")
        return texto


class TormentaSessaoCampanhaCreate(TormentaSessaoCampanhaBase):
    pass


class TormentaSessaoCampanhaUpdate(BaseModel):
    resumo: str | None = Field(default=None, min_length=1, max_length=4000)
    visivel_jogadores: bool | None = None

    @field_validator("resumo", mode="before")
    @classmethod
    def validar_resumo(cls, value):
        if value is None:
            return value
        texto = str(value).strip()
        if not texto:
            raise ValueError("Resumo da sessao nao pode ser vazio")
        return texto


class TormentaSessaoCampanhaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campanha_id: int
    campanha_nome: str = ""
    resumo: str
    visivel_jogadores: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None
