"""
Schemas Pydantic para Ataque e MagiaSlot
SRP: validação dos dados de entrada e saída
"""
from pydantic import BaseModel, Field
from typing import Optional


# ── Ataque 

class AtaqueBase(BaseModel):
    nome:         str = Field(..., min_length=1, max_length=100)
    bonus_ataque: str = Field(default="+0", max_length=20)
    dano:         str = Field(default="1d6",  max_length=30)
    tipo_dano:    str = Field(default="",     max_length=50)


class AtaqueCreate(AtaqueBase):
    pass


class AtaqueUpdate(BaseModel):
    nome:         Optional[str] = Field(None, min_length=1, max_length=100)
    bonus_ataque: Optional[str] = Field(None, max_length=20)
    dano:         Optional[str] = Field(None, max_length=30)
    tipo_dano:    Optional[str] = Field(None, max_length=50)


class AtaqueResponse(AtaqueBase):
    id:            int
    combatente_id: int

    class Config:
        from_attributes = True


# ── MagiaSlot 

class MagiaSlotBase(BaseModel):
    nivel:  int = Field(..., ge=0, le=9)
    total:  int = Field(default=0, ge=0)
    usados: int = Field(default=0, ge=0)


class MagiaSlotCreate(MagiaSlotBase):
    pass


class MagiaSlotUpdate(BaseModel):
    total:  Optional[int] = Field(None, ge=0)
    usados: Optional[int] = Field(None, ge=0)


class MagiaSlotResponse(MagiaSlotBase):
    id:            int
    combatente_id: int

    class Config:
        from_attributes = True


# ── Payload para salvar tudo de uma vez (Dashboard) ───────────────────────────

class AtaquesBulkRequest(BaseModel):
    """Substitui todos os ataques do combatente de uma só vez."""
    ataques: list[AtaqueCreate] = []


class MagiasBulkRequest(BaseModel):
    """Substitui todos os slots de magia do combatente de uma só vez."""
    slots: list[MagiaSlotCreate] = []