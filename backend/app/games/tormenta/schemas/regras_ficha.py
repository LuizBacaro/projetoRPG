"""Schemas — payload público de regras da ficha Tormenta 20."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class TormentaCustoAtributoItem(BaseModel):
    valor: int = Field(ge=0, le=99)
    custo: int


class TormentaPericiaAtributoItem(BaseModel):
    nome: str = Field(..., max_length=120)
    atributo: Optional[str] = Field(
        None,
        description="Chave do atributo: for, des, con, int, sab, car",
        max_length=3,
    )
    somente_treinado: bool = Field(
        default=False,
        description="Se true, a perícia só pode ser usada treinada (regra base T20).",
    )
    penalidade_armadura: bool = Field(
        default=False,
        description="Se true, a perícia sofre penalidade de armadura (regra base T20).",
    )


class TormentaRegrasAtributosResponse(BaseModel):
    pontos_compra_iniciais: int = Field(default=20, ge=0, le=999)
    custos: List[TormentaCustoAtributoItem]
    pericias: List[TormentaPericiaAtributoItem]


class TormentaRacaMbItem(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=120)
    ajustes: Dict[str, int] = Field(default_factory=dict)
    escolhe_duas_mais2: bool = False
    escolhe_um_mais2: bool = Field(
        default=False,
        description="Meio-orc: +2 em outra habilidade (excl. listadas em excluir_atributos_mais2).",
    )
    excluir_atributos_mais2: List[str] = Field(
        default_factory=list,
        description="Chaves for,des,con,int,sab,car excluídas do +2 opcional (ex.: int,car para meio-orc).",
    )
    mod_car_fixo: int = Field(default=0, ge=-10, le=10)
    tracos_resumo: str = Field(default="", max_length=8000)
    idioma_racial_mb: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Idioma próprio da raça no MB (null = só valkar + INT).",
    )


class TormentaIdiomaTabelaItem(BaseModel):
    idioma: str = Field(..., max_length=80)
    falantes: str = Field(default="", max_length=2000)


class TormentaRegrasRacasResponse(BaseModel):
    racas: List[TormentaRacaMbItem]
    idiomas_geral_mb: str = Field(
        default="",
        max_length=12000,
        description="Regra geral de idiomas e alfabetização (MB).",
    )
    idiomas_tabela_mb: List[TormentaIdiomaTabelaItem] = Field(default_factory=list)


class TormentaBeneficioNivelMbItem(BaseModel):
    nivel: int = Field(..., ge=1, le=40)
    xp_total: int = Field(..., ge=0, description="XP acumulado necessário para atingir este nível (MB).")
    graduacao_pericias: str = Field(default="", max_length=40)
    talentos_totais: int = Field(default=1, ge=0, le=30, description="Total de talentos do personagem neste nível (MB).")
    pontos_habilidade_acumulados: int = Field(
        default=0,
        ge=0,
        le=30,
        description="Pontos extras de habilidade acumulados (níveis pares no MB).",
    )
    bonus_meio_nivel: int = Field(
        default=0,
        ge=0,
        le=30,
        description="Metade do nível (arred. para baixo) somada à CA, resistências e dano (MB).",
    )


class TormentaClasseMbItem(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=80)
    abreviatura: str = Field(default="", max_length=8)
    bba_tipo: Literal["plein", "tres_quartos", "meio"] = Field(
        ...,
        description="plein = BBA igual ao nível de classe; tres_quartos; meio (mago/feiticeiro).",
    )
    pv_inicial: int = Field(..., ge=1, le=99)
    pv_por_nivel: int = Field(..., ge=0, le=30)
    pericias_treinadas: str = Field(default="", max_length=200)
    pericias_classe: str = Field(default="", max_length=2000)
    talentos_adicionais: str = Field(default="", max_length=2000)
    habilidades_por_nivel: Dict[str, str] = Field(
        default_factory=dict,
        description='Chaves "1".."20": texto MB deste nível (vazio = ver livro).',
    )


class TormentaRegrasClassesResponse(BaseModel):
    beneficios_por_nivel: List[TormentaBeneficioNivelMbItem]
    classes: List[TormentaClasseMbItem]
