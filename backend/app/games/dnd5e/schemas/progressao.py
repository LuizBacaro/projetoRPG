"""Schemas — progressão de personagem D&D 5e."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Dnd5eGerarAtributosRequest(BaseModel):
    metodo: str = Field(
        default="padrao",
        description="padrao | 4d6 | pontos",
        max_length=16,
    )
    seed: Optional[int] = Field(
        default=None,
        description="Semente opcional para reproduzir rolagem 4d6",
    )


class Dnd5eGerarAtributosResponse(BaseModel):
    metodo: str
    scores_base: Dict[str, int]
    pontos_gastos: Optional[int] = None
    orcamento_pontos: Optional[int] = None


class Dnd5eHpRollRequest(BaseModel):
    nivel: int = Field(..., ge=1, le=20)
    roll: Optional[int] = Field(
        default=None,
        ge=1,
        le=12,
        description="Valor rolado do dado de vida; omitir para rolar no servidor",
    )
    usar_media: bool = Field(
        default=False,
        description="Usar média arredondada para cima do dado de vida",
    )


class Dnd5eHpRollEntry(BaseModel):
    nivel: int = Field(ge=1, le=20)
    roll: int = Field(ge=1, le=12)
    con_mod: int
    ganho: int = Field(ge=1)
    usar_media: bool = False


class Dnd5eHpRollResponse(BaseModel):
    entrada: Dnd5eHpRollEntry
    hp_max: int = Field(ge=1)
    ficha: Dict[str, Any] = Field(default_factory=dict)


class Dnd5eMarcoRequest(BaseModel):
    nivel: int = Field(..., ge=1, le=20)
    tipo: str = Field(..., description="feat | asi", max_length=8)
    slug: Optional[str] = Field(
        default=None,
        max_length=80,
        description="Slug do feat quando tipo=feat",
    )
    distribuicao: Optional[Dict[str, int]] = Field(
        default=None,
        description="Distribuição ASI (+2 ou +1/+1) quando tipo=asi",
    )
    feat_escolhas: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Escolhas obrigatórias (resilient, magic_initiate) ao registrar feat",
    )


class Dnd5eFeatEscolhasRequest(BaseModel):
    feat_escolhas: Dict[str, Any] = Field(default_factory=dict)


class Dnd5eFeatEscolhasResponse(BaseModel):
    feat_escolhas: Dict[str, Any] = Field(default_factory=dict)
    ficha: Dict[str, Any] = Field(default_factory=dict)
    pendencias: List[str] = Field(default_factory=list)


class Dnd5ePericiasOverrideRequest(BaseModel):
    pericias_override: Dict[str, bool] = Field(default_factory=dict)


class Dnd5ePericiasOverrideResponse(BaseModel):
    pericias_override: Dict[str, bool] = Field(default_factory=dict)
    pericias_proficientes: List[str] = Field(default_factory=list)
    pericias_automaticas: List[str] = Field(default_factory=list)
    ficha: Dict[str, Any] = Field(default_factory=dict)
    pendencias: List[str] = Field(default_factory=list)


class Dnd5eExpertisePericiasRequest(BaseModel):
    expertise_pericias: List[str] = Field(default_factory=list)


class Dnd5eExpertisePericiasResponse(BaseModel):
    expertise_pericias: List[str] = Field(default_factory=list)
    expertise_efetiva: List[str] = Field(default_factory=list)
    expertise_slots_classe: int = Field(default=0, ge=0, le=8)
    ficha: Dict[str, Any] = Field(default_factory=dict)
    pendencias: List[str] = Field(default_factory=list)


class Dnd5eMarcoResponse(BaseModel):
    marco: Dict[str, Any]
    hp_max: int = Field(ge=1)
    hp_atual: int = Field(ge=0)
    hp_retroativo_con: int = Field(default=0, ge=0)
    ficha: Dict[str, Any] = Field(default_factory=dict)
    pendencias: List[str] = Field(default_factory=list)


class Dnd5ePendenciasProgressaoResponse(BaseModel):
    pendencias: List[str] = Field(default_factory=list)
    hp_max: int = Field(ge=1)
    hp_max_nivel_1: int = Field(ge=1)
    hp_resumo: Optional[Dict[str, Any]] = None
    marcos_pendentes: List[int] = Field(default_factory=list)
    niveis_hp_pendentes: List[int] = Field(default_factory=list)


class Dnd5eRepousoLongoCuraItem(BaseModel):
    nivel: int = Field(ge=2, le=20)
    roll: int = Field(ge=1, le=8)
    con_mod: int
    ganho: int = Field(ge=1)


class Dnd5eRepousoLongoResponse(BaseModel):
    hp_atual: int = Field(ge=0)
    hp_max: int = Field(ge=1)
    cura_total: int = Field(ge=0)
    cura_niveis: List[Dnd5eRepousoLongoCuraItem] = Field(default_factory=list)
    mensagem: str = Field(default="", max_length=500)
    conjuracao: Optional[Dict[str, Any]] = None
