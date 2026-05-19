"""Schemas — estado de conjuração na ficha (slots, preparação)."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Dnd5eSlotNivelItem(BaseModel):
    nivel: int = Field(ge=0, le=9)
    total: int = Field(ge=0)
    usados: int = Field(ge=0)
    disponiveis: int = Field(ge=0)


class Dnd5eConjuracaoEstadoResponse(BaseModel):
    classe: str
    nivel_personagem: int
    prepara_magias: bool = False
    magias_conhecidas_max: Optional[int] = None
    magias_conhecidas_atual: int = 0
    magias_preparadas_max: Optional[int] = None
    magias_preparadas_ids: List[int] = Field(default_factory=list)
    magias_lancadas_ids: List[int] = Field(default_factory=list)
    slots: List[Dnd5eSlotNivelItem] = Field(default_factory=list)
    magia_concentracao_id: Optional[int] = None
    recupera_slots_repouso_curto: bool = False


class Dnd5eConjuracaoGastarSlotRequest(BaseModel):
    # nivel_magia=0 representa truque (sem consumo de espaço, apenas marca a magia).
    nivel_magia: int = Field(..., ge=0, le=9)
    quantidade: int = Field(default=1, ge=1, le=9)
    magia_id: Optional[int] = Field(default=None, ge=1)


class Dnd5eConjuracaoPrepararRequest(BaseModel):
    magia_ids: List[int] = Field(default_factory=list)


class Dnd5eConjuracaoDescansoResponse(BaseModel):
    estado: Dnd5eConjuracaoEstadoResponse
    mensagem: str
