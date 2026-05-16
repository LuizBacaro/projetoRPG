"""Schemas — arena de combate D&D 5e (sessão leve)."""

from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class Dnd5eIniciativaCombatente(BaseModel):
    id: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=120)
    dex_mod: int = Field(default=0, ge=-5, le=20)


class Dnd5eIniciativaRequest(BaseModel):
    combatentes: List[Dnd5eIniciativaCombatente] = Field(..., min_length=1)


class Dnd5eIniciativaResultado(BaseModel):
    id: str
    nome: str
    dex_mod: int
    rolagem: int = Field(ge=1, le=20)
    iniciativa: int


class Dnd5eIniciativaResponse(BaseModel):
    ordem: List[Dnd5eIniciativaResultado]


class Dnd5eAtaqueRequest(BaseModel):
    mod_atributo: int = Field(default=0, ge=-5, le=20)
    bonus_proficiencia: int = Field(default=2, ge=2, le=6)
    ac_alvo: int = Field(..., ge=0, le=40)
    proficiente: bool = True
    bonus_extra: int = Field(default=0, ge=-20, le=20)
    rolagem_d20: Optional[int] = Field(None, ge=1, le=20)
    condicoes_atacante: List[str] = Field(default_factory=list)
    condicoes_alvo: List[str] = Field(default_factory=list)
    corpo_a_corpo: bool = True


class Dnd5eAtaqueResponse(BaseModel):
    rolagem: int
    rolagem_secundaria: Optional[int] = None
    total: int
    acerto: bool
    vantagem: bool = False
    desvantagem: bool = False
    critico_automatico: bool = False
    acerto_automatico: bool = False


class Dnd5eDanoRequest(BaseModel):
    dano: str = Field(default="1d8", max_length=20)
    mod_atributo: int = Field(default=0, ge=-5, le=20)
    is_critico: bool = False
    rolagem_forcada: Optional[int] = Field(
        None,
        ge=1,
        description="Soma forçada dos dados (testes)",
    )


class Dnd5eDanoResponse(BaseModel):
    dano_total: int = Field(ge=1)


class Dnd5eCondicaoAtivaItem(BaseModel):
    slug: str = Field(..., max_length=40)
    duracao_turnos: int = Field(
        default=-1,
        ge=-1,
        le=99,
        description="-1 permanente; 1+ turnos restantes do combatente",
    )
    origem: Optional[str] = Field(
        None,
        max_length=20,
        description='Ex.: "hp" para inconsciente automático a 0 PV',
    )


class Dnd5eCondicoesTurnoRequest(BaseModel):
    condicoes: List[Dnd5eCondicaoAtivaItem] = Field(default_factory=list)


class Dnd5eCondicoesTurnoResponse(BaseModel):
    condicoes: List[Dnd5eCondicaoAtivaItem]


class Dnd5eSincronizarHpCondicoesRequest(BaseModel):
    hp_atual: int = Field(..., ge=0)
    condicoes: List[Dnd5eCondicaoAtivaItem] = Field(default_factory=list)
