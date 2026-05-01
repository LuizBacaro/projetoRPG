"""Schemas Pydantic — ficha GURPS."""

from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class GurpsVantagemLinha(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(..., max_length=500)
    custo: int = 0


class GurpsDesvantagemLinha(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(..., max_length=500)
    custo: int = 0


class GurpsPericiaLinha(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    nome: str = Field(..., max_length=500)
    tipo: str = Field(..., max_length=20)
    nh: int = 0
    custo: int = 0


class GurpsPersonagemBase(BaseModel):
    tipo: str = Field(default="jogador", max_length=20)
    nome: str = Field(..., max_length=120)
    conceito: Optional[str] = Field(None, max_length=200)
    reacao: Optional[str] = Field(None, max_length=40)
    idade: Optional[str] = Field(None, max_length=80)
    campanha_id: Optional[int] = None
    iniciativa: int = 0

    st_custo: int = 0
    st_valor: int = 10
    dx_custo: int = 0
    dx_valor: int = 10
    iq_custo: int = 0
    iq_valor: int = 10
    ht_custo: int = 0
    ht_valor: int = 10
    vontade_custo: int = 0
    vontade_valor: int = 10
    percepcao_custo: int = 0
    percepcao_valor: int = 10
    pvs_custo: int = 0
    pvs_valor: int = 10
    pvs_atual: Optional[int] = None
    fadiga_custo: int = 0
    fadiga_valor: int = 10
    fadiga_atual: Optional[int] = None
    velocidade_custo: int = 0
    velocidade_valor: Decimal = Field(default=Decimal("5.00"))
    deslocamento_custo: int = 0
    deslocamento_valor: int = 5
    esquiva: int = 0
    aparar: int = 0
    bloqueio: Optional[str] = Field(None, max_length=20)
    dano_impacto: Optional[str] = Field(None, max_length=40)
    dano_balanco: Optional[str] = Field(None, max_length=40)
    pontos_atributos: int = 0
    pontos_vantagens: int = 0
    pontos_desvantagens: int = 0
    pontos_pericias: int = 0
    pontos_total: int = 0


class GurpsPersonagemCreate(GurpsPersonagemBase):
    vantagens: List[GurpsVantagemLinha] = Field(default_factory=list)
    desvantagens: List[GurpsDesvantagemLinha] = Field(default_factory=list)
    pericias: List[GurpsPericiaLinha] = Field(default_factory=list)


class GurpsPersonagemUpdate(BaseModel):
    tipo: Optional[str] = Field(None, max_length=20)
    nome: Optional[str] = Field(None, max_length=120)
    conceito: Optional[str] = Field(None, max_length=200)
    reacao: Optional[str] = Field(None, max_length=40)
    idade: Optional[str] = Field(None, max_length=80)
    campanha_id: Optional[int] = None
    iniciativa: Optional[int] = None
    foto_url: Optional[str] = Field(None, max_length=500)

    st_custo: Optional[int] = None
    st_valor: Optional[int] = None
    dx_custo: Optional[int] = None
    dx_valor: Optional[int] = None
    iq_custo: Optional[int] = None
    iq_valor: Optional[int] = None
    ht_custo: Optional[int] = None
    ht_valor: Optional[int] = None
    vontade_custo: Optional[int] = None
    vontade_valor: Optional[int] = None
    percepcao_custo: Optional[int] = None
    percepcao_valor: Optional[int] = None
    pvs_custo: Optional[int] = None
    pvs_valor: Optional[int] = None
    pvs_atual: Optional[int] = None
    fadiga_custo: Optional[int] = None
    fadiga_valor: Optional[int] = None
    fadiga_atual: Optional[int] = None
    velocidade_custo: Optional[int] = None
    velocidade_valor: Optional[Decimal] = None
    deslocamento_custo: Optional[int] = None
    deslocamento_valor: Optional[int] = None
    esquiva: Optional[int] = None
    aparar: Optional[int] = None
    bloqueio: Optional[str] = Field(None, max_length=20)
    dano_impacto: Optional[str] = Field(None, max_length=40)
    dano_balanco: Optional[str] = Field(None, max_length=40)
    pontos_atributos: Optional[int] = None
    pontos_vantagens: Optional[int] = None
    pontos_desvantagens: Optional[int] = None
    pontos_pericias: Optional[int] = None
    pontos_total: Optional[int] = None

    vantagens: Optional[List[GurpsVantagemLinha]] = None
    desvantagens: Optional[List[GurpsDesvantagemLinha]] = None
    pericias: Optional[List[GurpsPericiaLinha]] = None


class GurpsPersonagemResponse(GurpsPersonagemBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dono_id: Optional[int] = None
    foto_url: Optional[str] = None
    pvs_atual: int
    fadiga_atual: int
    vantagens: List[GurpsVantagemLinha] = Field(default_factory=list)
    desvantagens: List[GurpsDesvantagemLinha] = Field(default_factory=list)
    pericias: List[GurpsPericiaLinha] = Field(default_factory=list)
