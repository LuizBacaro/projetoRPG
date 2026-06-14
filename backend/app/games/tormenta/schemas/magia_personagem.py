"""Schemas — vínculos de magias MB na ficha Tormenta."""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

TormentaMagiaPapelMb = Literal["grimorio", "conhecida", "preparada"]


class TormentaMagiaVinculoCreate(BaseModel):
    magia_slug: str = Field(..., min_length=1, max_length=80)
    papel: TormentaMagiaPapelMb = Field(
        ...,
        description="grimorio = livro do mago; conhecida = espontâneo/lista; preparada = magias preparadas hoje.",
    )
    notas: Optional[str] = Field(None, max_length=500)


class TormentaMagiaPersonagemItem(BaseModel):
    id: int
    magia_slug: str
    papel: str
    nome: Optional[str] = Field(None, max_length=200)
    circulo: Optional[int] = Field(None, ge=0, le=20)
    tipo: Optional[str] = Field(None, max_length=20)
    escola: Optional[str] = Field(None, max_length=80)
    notas: Optional[str] = None
    adicionado_em: datetime


class TormentaMagiaLancarRequest(BaseModel):
    magia_slug: str = Field(..., min_length=1, max_length=80)


class TormentaMagiaLancarResponse(BaseModel):
    magia_slug: str
    custo_pm: int
    pa_atual_antes: int
    pa_atual_depois: int
    pa_max: Optional[int] = None
    permitido: bool
    motivo: str = ""
    truque_devocao: bool = False
    exige_concentracao: bool = False
    concentracao_ativa: Optional[str] = Field(
        None, description="Nome da magia em concentração após o lançamento."
    )


class TormentaMigrarMagiasJsonResponse(BaseModel):
    vinculos_criados: int = Field(..., ge=0, le=999)
    ignorados_duplicados: int = Field(..., ge=0, le=999)
    nao_encontrados: List[str] = Field(default_factory=list)


class TormentaEncerrarConcentracaoResponse(BaseModel):
    encerrada: bool = False
    concentracao_anterior: Optional[str] = None


class TormentaMagiaCirculoConhecidasItem(BaseModel):
    circulo: int = Field(..., ge=0, le=20)
    limite: int = Field(..., ge=0, le=99)
    usadas: int = Field(..., ge=0, le=99)


class TormentaMagiasConhecidasPreviewResponse(BaseModel):
    classe_slug: str = Field(default="", max_length=40)
    nivel: int = Field(default=1, ge=1, le=40)
    usa_limite_conhecidas: bool = False
    total_conhecidas_usadas: int = Field(default=0, ge=0, le=999)
    total_conhecidas_max: Optional[int] = Field(default=None, ge=0, le=999)
    por_circulo: List[TormentaMagiaCirculoConhecidasItem] = Field(default_factory=list)
    circulo_max_lancavel: int = Field(default=0, ge=0, le=20)
    bardo_pode_trocar: bool = False
    niveis_troca_bardo: List[int] = Field(default_factory=list)


class TormentaMagiasGrimorioPreviewResponse(BaseModel):
    classe_slug: str = Field(default="", max_length=40)
    nivel: int = Field(default=1, ge=1, le=40)
    usa_limite_grimorio: bool = False
    grimorio_usadas: int = Field(default=0, ge=0, le=999)
    grimorio_max: Optional[int] = Field(default=None, ge=0, le=999)
    truques_no_livro: int = Field(default=0, ge=0, le=999)
    truques_contam_orcamento: bool = False
    circulo_max_lancavel: int = Field(default=0, ge=0, le=20)


class TormentaMagiasPreparadasPreviewResponse(BaseModel):
    classe_slug: str = Field(default="", max_length=40)
    nivel: int = Field(default=1, ge=1, le=40)
    usa_limite_preparadas: bool = False
    preparadas_usadas: int = Field(default=0, ge=0, le=999)
    preparadas_max: Optional[int] = Field(default=None, ge=0, le=999)
    mod_habilidade_chave: int = Field(default=0, ge=-20, le=20)
    truques_contam_teto: bool = False
    exige_grimorio: bool = True
    exige_repertorio: bool = False


class TormentaMagiasRepertorioPreviewResponse(BaseModel):
    classe_slug: str = Field(default="", max_length=40)
    nivel: int = Field(default=1, ge=1, le=40)
    usa_limite_repertorio: bool = False
    repertorio_usadas: int = Field(default=0, ge=0, le=999)
    repertorio_max: Optional[int] = Field(default=None, ge=0, le=999)
    truques_no_repertorio: int = Field(default=0, ge=0, le=999)
    truques_contam_orcamento: bool = False
    circulo_max_lancavel: int = Field(default=0, ge=0, le=20)


class TormentaMagiasLimparPreparadasResponse(BaseModel):
    removidas: int = Field(..., ge=0, le=999)


class TormentaMagiaTrocaRequest(BaseModel):
    magia_slug_removida: str = Field(..., min_length=1, max_length=80)
    magia_slug_nova: str = Field(..., min_length=1, max_length=80)
    notas: Optional[str] = Field(None, max_length=500)


class TormentaMagiaTrocaResponse(BaseModel):
    removida_slug: str
    nova_slug: str
    vinculo: TormentaMagiaPersonagemItem
