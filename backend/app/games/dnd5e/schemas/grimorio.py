"""Schemas — grimório D&D 5e (paridade com dnd35)."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class Dnd5eGrimorioMagiaCreate(BaseModel):
    magia_id: int
    classe: str = Field(..., min_length=1, max_length=50)
    origem: str = Field(default="SELECAO_MANUAL", max_length=30)


class Dnd5eGrimorioMagiaUpdate(BaseModel):
    favorita: Optional[bool] = None
    anotacoes: Optional[str] = None


class Dnd5eGrimorioMagiaResponse(BaseModel):
    id: int
    personagem_id: int
    magia_id: int
    classe: str
    favorita: bool
    anotacoes: Optional[str] = None
    origem: str
    adicionada_em: datetime

    magia_nome: Optional[str] = None
    magia_dano: Optional[str] = None
    magia_ataque_magico: Optional[str] = None
    magia_escola: Optional[str] = None
    magia_nivel: Optional[int] = None
    magia_componentes: Optional[str] = None
    descricao: Optional[str] = None
    descricao_nivel_superior: Optional[str] = None
    tempo_conjuracao: Optional[str] = None
    alcance_texto: Optional[str] = None
    duracao: Optional[str] = None
    requer_concentracao: bool = False
    ritual: bool = False
    material_consumido: bool = False
    componentes_material: Optional[str] = None
    teste_resistencia: Optional[str] = None

    class Config:
        from_attributes = True


class Dnd5eGrimorioTrocaRequest(BaseModel):
    classe: str = Field(..., min_length=1, max_length=50)
    magia_removida_id: int
    magia_adicionada_id: int


class Dnd5eGrimorioTrocaResponse(BaseModel):
    personagem_id: int
    combatente_id: int
    classe: str
    magia_removida_id: int
    magia_adicionada_id: int
    nivel_personagem: int
    realizada_em: datetime


class Dnd5eGrimorioHistoricoTrocaResponse(BaseModel):
    id: int
    personagem_id: int
    combatente_id: int
    classe: str
    magia_removida_id: int
    magia_adicionada_id: int
    nivel_personagem: int
    realizada_em: datetime
    magia_removida_nome: Optional[str] = None
    magia_adicionada_nome: Optional[str] = None


class Dnd5eGrimorioNotificacaoResponse(BaseModel):
    id: int
    personagem_id: int
    combatente_id: int
    classe: str
    tipo: str
    dados: dict[str, Any] = Field(default_factory=dict)
    lida: bool
    criada_em: datetime


class Dnd5eGrimorioNotificacaoUpdate(BaseModel):
    lida: bool = True


class Dnd5eMagiaImportPreviewResponse(BaseModel):
    import_id: str
    total_linhas: int
    validas: int
    erros: list[dict[str, Any]] = Field(default_factory=list)
    amostra: list[dict[str, Any]] = Field(default_factory=list)


class Dnd5eMagiaImportConfirmRequest(BaseModel):
    import_id: str


class Dnd5eMagiaImportConfirmResponse(BaseModel):
    importadas: int
    atualizadas: int
    vinculos_ignorados: int = 0
