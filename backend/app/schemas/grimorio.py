"""Schemas do módulo Grimório."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class GrimorioMagiaCreate(BaseModel):
    magia_id: int
    classe: str = Field(..., min_length=1, max_length=50)
    origem: str = Field(default="SELECAO_MANUAL", max_length=30)


class GrimorioMagiaUpdate(BaseModel):
    favorita: Optional[bool] = None
    anotacoes: Optional[str] = None


class GrimorioMagiaResponse(BaseModel):
    id: int
    combatente_id: int
    magia_id: int
    classe: str
    favorita: bool
    anotacoes: Optional[str]
    origem: str
    adicionada_em: datetime

    magia_nome: Optional[str] = None
    magia_escola: Optional[str] = None
    magia_nivel: Optional[int] = None
    magia_componentes: Optional[str] = None
    magia_e_magia_dominio: bool = False
    magia_dominios: Optional[str] = None

    class Config:
        from_attributes = True


class GrimorioTrocaRequest(BaseModel):
    classe: str = Field(..., min_length=1, max_length=50)
    magia_removida_id: int
    magia_adicionada_id: int


class GrimorioTrocaResponse(BaseModel):
    combatente_id: int
    classe: str
    magia_removida_id: int
    magia_adicionada_id: int
    nivel_personagem: int
    realizada_em: datetime


class GrimorioHistoricoTrocaResponse(BaseModel):
    id: int
    combatente_id: int
    classe: str
    magia_removida_id: int
    magia_adicionada_id: int
    nivel_personagem: int
    realizada_em: datetime
    magia_removida_nome: Optional[str] = None
    magia_adicionada_nome: Optional[str] = None


class GrimorioNotificacaoResponse(BaseModel):
    id: int
    combatente_id: int
    classe: str
    tipo: str
    dados: dict = Field(default_factory=dict)
    lida: bool
    criada_em: datetime


class GrimorioNotificacaoUpdate(BaseModel):
    lida: bool = True
