"""Schemas Pydantic de Sessão de Campanha (D&D 3.5) — canônico em `app.games.dnd35.schemas.sessao_campanha`."""

from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class SessaoCampanhaBase(BaseModel):
    campanha_id: int = Field(..., ge=1)
    resumo: str = Field(..., min_length=1, max_length=4000)
    visivel_jogadores: bool = False

    @field_validator("resumo", mode="before")
    @classmethod
    def validar_resumo(cls, value):
        texto = str(value or "").strip()
        if not texto:
            raise ValueError("Resumo da sessão é obrigatório")
        return texto


class SessaoCampanhaCreate(SessaoCampanhaBase):
    pass


class SessaoCampanhaUpdate(BaseModel):
    resumo: str | None = Field(default=None, min_length=1, max_length=4000)
    visivel_jogadores: bool | None = None

    @field_validator("resumo", mode="before")
    @classmethod
    def validar_resumo(cls, value):
        if value is None:
            return value
        texto = str(value).strip()
        if not texto:
            raise ValueError("Resumo da sessão não pode ser vazio")
        return texto


class SessaoCampanhaResponse(BaseModel):
    id: int
    campanha_id: int
    campanha_nome: str = ""
    resumo: str
    visivel_jogadores: bool = False
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True
