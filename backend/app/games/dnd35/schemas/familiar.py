from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FamiliarEspecieItem(BaseModel):
    slug: str
    nome: str
    categoria: str
    bonus_mestre: str
    deslocamento: str
    atributos_base: Dict[str, int]
    armadura_natural_base: int = 0
    hp_extra_mestre: int = 0


class FamiliarElegibilidadeResponse(BaseModel):
    elegivel: bool
    motivo: str = ""
    nivel_mestre: int = 0
    classe: str = ""
    nivel_personagem: int = 1


class FamiliarCalcularRequest(BaseModel):
    especie_slug: str = Field(..., min_length=1, max_length=60)
    nome: str = Field("Familiar", min_length=1, max_length=120)


class FamiliarEstatisticasDerivadas(BaseModel):
    nivel_mestre: int
    inteligencia: int
    armadura_natural_base: int
    armadura_natural_bonus: int
    armadura_natural_total: int
    atributos_base: Dict[str, int]
    modificadores: Dict[str, int]
    ca: int
    hp_max_sugerido: int
    hp_extra_mestre: int = 0
    habilidades_especiais: List[str]
    resistencia_magia: Optional[int] = None
    bonus_mestre_especie: str = ""


class FamiliarCalcularResponse(BaseModel):
    especie: FamiliarEspecieItem
    elegibilidade: FamiliarElegibilidadeResponse
    derivadas: FamiliarEstatisticasDerivadas


class FamiliarBase(BaseModel):
    especie_slug: str = Field(..., min_length=1, max_length=60)
    nome: str = Field(..., min_length=1, max_length=120)
    nivel_mestre: int = Field(1, ge=1, le=30)
    inteligencia: int = Field(6, ge=1, le=30)
    armadura_natural_bonus: int = Field(1, ge=0, le=20)
    hp_atual: int = Field(1, ge=0, le=9999)
    hp_maximo: int = Field(1, ge=1, le=9999)
    ca: int = Field(10, ge=0, le=99)
    bonus_mestre: str = Field("", max_length=200)
    habilidades_especiais: List[str] = Field(default_factory=list)
    anotacoes: Optional[str] = Field(None, max_length=8000)


class FamiliarUpsert(FamiliarBase):
    pass


class FamiliarResponse(FamiliarBase):
    id: int
    combatente_id: int
    especie_nome: str = ""
    derivadas: Optional[FamiliarEstatisticasDerivadas] = None
    elegibilidade: Optional[FamiliarElegibilidadeResponse] = None

    class Config:
        from_attributes = True
