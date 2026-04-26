"""
Schemas de DivindadeCustom (D&D 3.5)
SRP: define contrato de entrada/saida das divindades de campanha.

Canônico: `app.games.dnd35.schemas.divindade_custom`.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class DivindadeCustomBase(BaseModel):
    """Campos comuns de DivindadeCustom."""

    nome: str = Field(..., min_length=1, max_length=100)
    titulo: str = Field("", max_length=200)
    tendencia: str = Field(..., min_length=1, max_length=50)
    dominios: List[str] = Field(
        default_factory=list,
        description="Lista de dominios canonicos (ex.: ['Bem', 'Protecao', 'Guerra']).",
    )
    descricao: Optional[str] = None

    @field_validator("nome", "titulo", "tendencia", "descricao", mode="before")
    @classmethod
    def _strip_strings(cls, v):
        if v is None:
            return v
        return str(v).strip()

    @field_validator("dominios", mode="before")
    @classmethod
    def _coerce_dominios(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            return [item.strip() for item in v.split(",") if item.strip()]
        if isinstance(v, (list, tuple, set)):
            return [str(item).strip() for item in v if str(item).strip()]
        return []


class DivindadeCustomCreate(DivindadeCustomBase):
    """Payload de criacao."""


class DivindadeCustomResponse(DivindadeCustomBase):
    """Representacao completa (inclui id, metadata e rotulo pronto para UI)."""

    id: int
    label: str
    criado_por_id: Optional[int] = None
    criado_em: Optional[datetime] = None
    origem: str = "custom"

    class Config:
        from_attributes = True
