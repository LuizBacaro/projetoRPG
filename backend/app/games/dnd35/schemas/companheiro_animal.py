from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

CHAVES_ATRIBUTO = (
    "forca",
    "destreza",
    "constituicao",
    "inteligencia",
    "sabedoria",
    "carisma",
)


class CompanheiroEspecieItem(BaseModel):
    slug: str
    nome: str
    categoria: str
    hd_base: int
    armadura_natural_base: int
    deslocamento: str
    atributos_base: Dict[str, int]
    ataque_padrao: str = ""


class CompanheiroElegibilidadeResponse(BaseModel):
    elegivel: bool
    motivo: str = ""
    nivel_efetivo: int = 0
    classe: str = ""
    nivel_personagem: int = 1


class CompanheiroCalcularRequest(BaseModel):
    especie_slug: str = Field(..., min_length=1, max_length=60)
    bonus_atributos: Dict[str, int] = Field(default_factory=dict)
    nome: str = Field("Companheiro", min_length=1, max_length=120)

    @field_validator("bonus_atributos")
    @classmethod
    def _validar_bonus(cls, v: Dict[str, int]) -> Dict[str, int]:
        out = {}
        for k, val in (v or {}).items():
            if k in CHAVES_ATRIBUTO:
                out[k] = int(val)
        return out


class CompanheiroEstatisticasDerivadas(BaseModel):
    nivel_efetivo: int
    hd_bonus: int
    hd_total: int
    atributos_efetivos: Dict[str, int]
    modificadores: Dict[str, int]
    bab: int
    fortitude: int
    reflexos: int
    vontade: int
    armadura_natural_base: int
    armadura_natural_vinculo: int
    armadura_natural_total: int
    ca: int
    hp_max_sugerido: int
    talentos_total: int
    truques_bonus: int
    distribuicao_atributos: str
    habilidades_especiais: List[str]


class CompanheiroCalcularResponse(BaseModel):
    especie: CompanheiroEspecieItem
    elegibilidade: CompanheiroElegibilidadeResponse
    derivadas: CompanheiroEstatisticasDerivadas


class CompanheiroAnimalBase(BaseModel):
    especie_slug: str = Field(..., min_length=1, max_length=60)
    nome: str = Field(..., min_length=1, max_length=120)
    forca: int = Field(3, ge=1, le=50)
    destreza: int = Field(3, ge=1, le=50)
    constituicao: int = Field(3, ge=1, le=50)
    inteligencia: int = Field(1, ge=1, le=50)
    sabedoria: int = Field(3, ge=1, le=50)
    carisma: int = Field(1, ge=1, le=50)
    bonus_atributos: Dict[str, int] = Field(default_factory=dict)
    hp_atual: int = Field(1, ge=0, le=9999)
    hp_maximo: int = Field(1, ge=1, le=9999)
    ca: int = Field(10, ge=0, le=99)
    iniciativa: Optional[int] = None
    deslocamento: Optional[str] = Field(None, max_length=80)
    truques: List[str] = Field(default_factory=list)
    talentos: List[str] = Field(default_factory=list)
    pericias: List[Any] = Field(default_factory=list)
    ataques: List[Any] = Field(default_factory=list)
    anotacoes: Optional[str] = Field(None, max_length=8000)


class CompanheiroAnimalUpsert(CompanheiroAnimalBase):
    pass


class CompanheiroAnimalResponse(CompanheiroAnimalBase):
    id: int
    combatente_id: int
    especie_nome: str = ""
    derivadas: Optional[CompanheiroEstatisticasDerivadas] = None
    elegibilidade: Optional[CompanheiroElegibilidadeResponse] = None

    class Config:
        from_attributes = True
