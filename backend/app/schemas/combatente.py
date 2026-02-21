"""
Schemas Pydantic para Combatente (DTOs)
"""
from pydantic import BaseModel, Field
from typing import Optional


class CombatenteBase(BaseModel):
    """Schema base para Combatente"""
    nome: str = Field(..., min_length=1, max_length=100)
    tipo: str = Field(..., pattern="^(jogador|monstro|npc)$")
    classe: str = Field(..., min_length=1, max_length=50)
    hp_maximo: int = Field(..., gt=0)
    iniciativa: int = Field(..., ge=0)

    # Defesa
    ca: int = Field(default=10, ge=0, le=50)
    toque: int = Field(default=10, ge=0, le=50)
    surpresa: int = Field(default=10, ge=0, le=50)

    # Atributos D&D
    forca: int = Field(default=10, ge=1, le=30)
    destreza: int = Field(default=10, ge=1, le=30)
    constituicao: int = Field(default=10, ge=1, le=30)
    inteligencia: int = Field(default=10, ge=1, le=30)
    sabedoria: int = Field(default=10, ge=1, le=30)
    carisma: int = Field(default=10, ge=1, le=30)

    # Resistências
    fortitude: int = Field(default=0, ge=-10, le=50)
    reflexos: int = Field(default=0, ge=-10, le=50)
    vontade: int = Field(default=0, ge=-10, le=50)

    # Progressão
    nivel: int = Field(default=1, ge=1, le=20)
    pontos: int = Field(default=0, ge=0)


class CombatenteCreate(CombatenteBase):
    """Schema para criação de Combatente"""
    foto_url: Optional[str] = None


class CombatenteUpdate(BaseModel):
    """Schema para atualização de Combatente"""
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    tipo: Optional[str] = Field(None, pattern="^(jogador|monstro|npc)$")
    classe: Optional[str] = Field(None, min_length=1, max_length=50)
    hp_atual: Optional[int] = Field(None, ge=0)
    hp_maximo: Optional[int] = Field(None, gt=0)
    iniciativa: Optional[int] = Field(None, ge=0)
    foto_url: Optional[str] = None

    # Defesa
    ca: Optional[int] = Field(None, ge=0, le=50)
    toque: Optional[int] = Field(None, ge=0, le=50)
    surpresa: Optional[int] = Field(None, ge=0, le=50)

    # Atributos D&D
    forca: Optional[int] = Field(None, ge=1, le=30)
    destreza: Optional[int] = Field(None, ge=1, le=30)
    constituicao: Optional[int] = Field(None, ge=1, le=30)
    inteligencia: Optional[int] = Field(None, ge=1, le=30)
    sabedoria: Optional[int] = Field(None, ge=1, le=30)
    carisma: Optional[int] = Field(None, ge=1, le=30)

    # Resistências
    fortitude: Optional[int] = Field(None, ge=-10, le=50)
    reflexos: Optional[int] = Field(None, ge=-10, le=50)
    vontade: Optional[int] = Field(None, ge=-10, le=50)

    nivel: Optional[int] = Field(None, ge=1, le=20)
    pontos: Optional[int] = Field(None, ge=0)


class CombatenteResponse(CombatenteBase):
    """Schema de resposta para Combatente"""
    id: int
    hp_atual: int
    foto_url: Optional[str] = None

    class Config:
        from_attributes = True


class HPUpdateRequest(BaseModel):
    """Schema para atualização de HP"""
    hp_atual: int = Field(..., ge=0)


class IniciativaUpdateRequest(BaseModel):
    """Schema para atualização de Iniciativa"""
    iniciativa: int = Field(..., ge=0)


class DanoRequest(BaseModel):
    """Schema para aplicação de dano"""
    dano: int = Field(..., gt=0)


class DanoCuraRequest(BaseModel):
    """Schema para requisição de dano/cura"""
    valor: int = Field(..., gt=0, description="Valor do dano ou cura (deve ser maior que 0)")

    class Config:
        json_schema_extra = {"example": {"valor": 10}}


class DanoCuraResponse(BaseModel):
    """Schema de resposta para aplicação de dano/cura"""
    id: int
    nome: str
    hp_atual: int
    hp_maximo: int
    mensagem: str

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "nome": "Theron",
                "hp_atual": 90,
                "hp_maximo": 100,
                "mensagem": "Theron sofreu 10 de dano"
            }
        }