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
    descricao: Optional[str] = None
    sub_escola: Optional[str] = None
    area_efeito: Optional[str] = None
    resistencia_magia: Optional[str] = None

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


class GrimorioDiagnosticoMagiaResponse(BaseModel):
    magia_id: int
    magia_nome: str
    magia_nivel: int
    classe: str
    magia_e_magia_dominio: bool = False
    magia_dominios: Optional[str] = None
    ja_no_grimorio: bool = False
    bloqueada_por_alinhamento: bool = False
    bloqueada_por_dominio: bool = False
    bloqueada_por_dominio_oposto: bool = False
    permitida: bool
    motivos_bloqueio: list[str] = Field(default_factory=list)


class GrimorioDiagnosticoResponse(BaseModel):
    combatente_id: int
    classe: str
    alinhamento: Optional[str] = None
    dominios_personagem: list[str] = Field(default_factory=list)
    total_magias_avaliadas: int
    total_permitidas: int
    total_bloqueadas: int
    itens: list[GrimorioDiagnosticoMagiaResponse] = Field(default_factory=list)
