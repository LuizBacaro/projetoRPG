"""Schemas do bestiário D&D 3.5 (Livro dos Monstros)."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DnD35BestiarioResumo(BaseModel):
    slug: str
    nome: str
    nd: Optional[float] = None
    nd_rotulo: Optional[str] = None
    tipo_criatura: Optional[str] = None
    tamanho: Optional[str] = None
    hp_maximo: Optional[int] = None
    ca: Optional[int] = None
    toque: Optional[int] = None
    surpresa: Optional[int] = None
    pagina_referencia: Optional[str] = None
    fonte: str = "mm35"
    especie_pai: Optional[str] = None
    categoria_idade: Optional[str] = None
    descricao_curta: str = ""


class DnD35BestiarioDetalhe(DnD35BestiarioResumo):
    subtipos: List[str] = Field(default_factory=list)
    dv: Optional[str] = None
    iniciativa: Optional[int] = None
    deslocamento: Optional[str] = None
    ataque_base: Optional[str] = None
    agarrar: Optional[str] = None
    fortitude: Optional[int] = None
    reflexos: Optional[int] = None
    vontade: Optional[int] = None
    for_valor: Optional[int] = None
    des_valor: Optional[int] = None
    con_valor: Optional[int] = None
    int_valor: Optional[int] = None
    sab_valor: Optional[int] = None
    car_valor: Optional[int] = None
    ataques: List[Dict[str, Any]] = Field(default_factory=list)
    ataque_total: Optional[str] = None
    espaco_alcance: Optional[str] = None
    ataques_especiais: List[str] = Field(default_factory=list)
    qualidades_especiais: List[str] = Field(default_factory=list)
    pericias_resumo: str = ""
    talentos_resumo: str = ""
    ambiente: str = ""
    organizacao: str = ""
    tesouro: str = ""
    tendencia: str = ""
    progressao: str = ""
    ajuste_nivel: str = ""
    aliases: List[str] = Field(default_factory=list)


class DnD35BestiarioPagina(BaseModel):
    itens: List[DnD35BestiarioResumo]
    total: int
    skip: int
    limit: int


class DnD35BestiarioImportRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    slug: str = Field(..., min_length=1, max_length=80)
    tipo: str = Field(default="monstro", pattern="^(monstro|npc)$")
    campanha_id: Optional[int] = Field(default=None, ge=1)
    nome_override: Optional[str] = Field(default=None, max_length=100)
    foto_url: Optional[str] = Field(default=None, max_length=500)
