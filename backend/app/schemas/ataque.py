"""
Schemas Pydantic para Ataque, MagiaSlot e MagiaPreparada
SRP: apenas serialização/validação
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# ── Ataque ──

class AtaqueBase(BaseModel):
    nome:         str
    bonus_ataque: str           = "+0"
    dano:         str           = "1d6"
    tipo_dano:    Optional[str] = ""

class AtaqueCreate(AtaqueBase):
    pass

class AtaqueResponse(AtaqueBase):
    id:            int
    combatente_id: int
    class Config:
        from_attributes = True

class AtaquesBulkRequest(BaseModel):
    ataques: List[AtaqueCreate]


# ── MagiaSlot ──

class MagiaSlotBase(BaseModel):
    nivel:  int
    total:  int = 0
    usados: int = 0

class MagiaSlotCreate(MagiaSlotBase):
    pass

class MagiaSlotUpdate(BaseModel):
    usados: int

class MagiaSlotResponse(MagiaSlotBase):
    id:            int
    combatente_id: int
    class Config:
        from_attributes = True

class MagiasBulkRequest(BaseModel):
    slots: List[MagiaSlotCreate]


# ── MagiaPreparada ──

class MagiaPreparadaCreate(BaseModel):
    magia_id:   int
    nivel_slot: int
    classe:     Optional[str] = None

class MagiaPreparadaResponse(BaseModel):
    id:            int
    combatente_id: int
    magia_id:      int
    nivel_slot:    int
    usada:         bool              = False    # ✅ NOVO
    preparada_em:  Optional[datetime] = None
    magia_nome:    Optional[str]      = None
    magia_escola:  Optional[str]      = None
    magia_nivel:   Optional[int]      = None
    class Config:
        from_attributes = True

class DescansoRequest(BaseModel):
    confirmar: bool = True