"""
Schemas Pydantic para Combatente (DTOs)
SRP: apenas serialização/validação
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from .ataque import AtaqueResponse, MagiaSlotResponse, MagiaPreparadaResponse


class CombatenteBase(BaseModel):
    nome:       str = Field(..., min_length=1, max_length=100)
    tipo:       str = Field(..., pattern="^(jogador|monstro|npc)$")
    classe:     str = Field(..., min_length=1, max_length=50)
    raca:       Optional[str] = Field(default="", max_length=50)

    # ✅ NOVO: apenas monstros usam, mas aceita em todos os tipos (nullable)
    pagina_referencia: Optional[str] = Field(default="", max_length=100)

    hp_maximo:  int = Field(..., gt=0)
    iniciativa: int = Field(..., ge=0)

    ca:       int = Field(default=10, ge=0, le=50)
    toque:    int = Field(default=10, ge=0, le=50)
    surpresa: int = Field(default=10, ge=0, le=50)

    forca:        int = Field(default=10, ge=1, le=30)
    destreza:     int = Field(default=10, ge=1, le=30)
    constituicao: int = Field(default=10, ge=1, le=30)
    inteligencia: int = Field(default=10, ge=1, le=30)
    sabedoria:    int = Field(default=10, ge=1, le=30)
    carisma:      int = Field(default=10, ge=1, le=30)

    fortitude: int = Field(default=0, ge=-10, le=50)
    reflexos:  int = Field(default=0, ge=-10, le=50)
    vontade:   int = Field(default=0, ge=-10, le=50)

    nivel:  int = Field(default=1,  ge=1, le=20)
    pontos: int = Field(default=0,  ge=0)


class CombatenteCreate(CombatenteBase):
    foto_url: Optional[str] = None


class CombatenteUpdate(BaseModel):
    nome:       Optional[str] = Field(None, min_length=1, max_length=100)
    tipo:       Optional[str] = Field(None, pattern="^(jogador|monstro|npc)$")
    classe:     Optional[str] = Field(None, min_length=1, max_length=50)
    raca:       Optional[str] = Field(None, max_length=50)

    # ✅ NOVO
    pagina_referencia: Optional[str] = Field(None, max_length=100)

    hp_atual:   Optional[int] = Field(None, ge=0)
    hp_maximo:  Optional[int] = Field(None, gt=0)
    iniciativa: Optional[int] = Field(None, ge=0)
    foto_url:   Optional[str] = None

    ca:       Optional[int] = Field(None, ge=0, le=50)
    toque:    Optional[int] = Field(None, ge=0, le=50)
    surpresa: Optional[int] = Field(None, ge=0, le=50)

    forca:        Optional[int] = Field(None, ge=1, le=30)
    destreza:     Optional[int] = Field(None, ge=1, le=30)
    constituicao: Optional[int] = Field(None, ge=1, le=30)
    inteligencia: Optional[int] = Field(None, ge=1, le=30)
    sabedoria:    Optional[int] = Field(None, ge=1, le=30)
    carisma:      Optional[int] = Field(None, ge=1, le=30)

    fortitude: Optional[int] = Field(None, ge=-10, le=50)
    reflexos:  Optional[int] = Field(None, ge=-10, le=50)
    vontade:   Optional[int] = Field(None, ge=-10, le=50)

    nivel:  Optional[int] = Field(None, ge=1, le=20)
    pontos: Optional[int] = Field(None, ge=0)


class CombatenteResponse(CombatenteBase):
    id:       int
    hp_atual: int
    foto_url: Optional[str] = None
    raca:     Optional[str] = ""

    # ✅ NOVO: exposto no response para o frontend exibir na ficha/arena
    pagina_referencia: Optional[str] = ""

    ataques:           List[AtaqueResponse]         = []
    magias_slots:      List[MagiaSlotResponse]      = []
    magias_preparadas: List[MagiaPreparadaResponse] = []

    class Config:
        from_attributes = True


class HPUpdateRequest(BaseModel):
    hp_atual: int = Field(..., ge=0)

class IniciativaUpdateRequest(BaseModel):
    iniciativa: int = Field(..., ge=0)

class DanoRequest(BaseModel):
    dano: int = Field(..., gt=0)

class DanoCuraRequest(BaseModel):
    valor: int = Field(..., gt=0)
    class Config:
        json_schema_extra = {"example": {"valor": 10}}

class DanoCuraResponse(BaseModel):
    id:        int
    nome:      str
    hp_atual:  int
    hp_maximo: int
    mensagem:  str
    class Config:
        from_attributes = True