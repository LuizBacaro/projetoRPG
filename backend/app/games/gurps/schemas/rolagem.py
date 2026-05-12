"""Schemas de rolagem GURPS (3d6)."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class GurpsTeste3d6Request(BaseModel):
    nivel_efetivo: int = Field(..., ge=1, le=30)
    dados: Optional[List[int]] = Field(
        default=None,
        description="Opcional para debug/teste; informe 3 valores de 1 a 6.",
    )


class GurpsTeste3d6Response(BaseModel):
    dados: List[int]
    total: int
    nivel_efetivo: int
    sucesso: bool
    margem: int
    sucesso_decisivo: bool
    falha_critica: bool


class GurpsNivelEfetivoRequest(BaseModel):
    nh_base: int = Field(..., ge=1, le=30)
    modificadores: List[int] = Field(
        default_factory=list,
        description="Modificadores situacionais somados ao NH base (podem ser negativos).",
    )


class GurpsNivelEfetivoResponse(BaseModel):
    nh_base: int
    modificadores: List[int]
    soma_modificadores: int
    nivel_efetivo: int


class GurpsDanoRequest(BaseModel):
    expressao: str = Field(
        ...,
        description="Expressão de dano no formato Nd, Nd+M ou Nd-M (ex.: 2d+1, 1d-2).",
    )


class GurpsDanoResponse(BaseModel):
    expressao: str
    dados_rolados: List[int]
    quantidade_dados: int
    modificador: int
    total_sem_modificador: int
    total: int
