"""Schemas — payload público de regras D&D 5e (ficha)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class Dnd5eHabilidadeMetaItem(BaseModel):
    chave: str = Field(
        ...,
        max_length=20,
        description="Chave API: strength, dexterity, constitution, intelligence, wisdom, charisma",
    )
    nome: str = Field(..., max_length=40)
    abreviacao_en: str = Field(..., max_length=4)
    abreviacao_pt: str = Field(..., max_length=4)


class Dnd5eBonusProficienciaItem(BaseModel):
    nivel_min: int = Field(ge=1, le=20)
    nivel_max: int = Field(ge=1, le=20)
    bonus: int = Field(ge=0, le=20)


class Dnd5eRegrasAtributosResponse(BaseModel):
    habilidade_min: int = Field(ge=1, le=30)
    habilidade_max: int = Field(ge=1, le=30)
    nivel_min: int = Field(ge=1, le=30)
    nivel_max: int = Field(ge=1, le=30)
    formula_modificador: str = Field(
        default="(valor - 10) // 2",
        description="Modificador PHB (arredondado para baixo).",
    )
    habilidades: List[Dnd5eHabilidadeMetaItem]
    bonus_proficiencia_por_nivel: List[Dnd5eBonusProficienciaItem]


class Dnd5eRacaItem(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=80)
    tamanho: str = Field(..., max_length=20)
    velocidade_metros: float = Field(ge=0, le=60)
    bonus_habilidades: Dict[str, int] = Field(default_factory=dict)
    tracos_resumo: str = Field(default="", max_length=4000)
    caracteristicas: List[str] = Field(default_factory=list)
    escolhe_duas_mais1: bool = False


class Dnd5eRegrasRacasResponse(BaseModel):
    racas: List[Dnd5eRacaItem]


class Dnd5eClasseItem(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=80)
    dado_vida: str = Field(..., max_length=4)
    habilidade_primaria: str = Field(..., max_length=40)
    habilidade_primaria_chave: str = Field(..., max_length=20)
    salvamentos: List[str] = Field(default_factory=list)
    pericias_escolha_qtd: int = Field(default=0, ge=0, le=10)
    pericias_escolha_de: List[str] = Field(default_factory=list)
    armaduras: List[str] = Field(default_factory=list)
    armas: List[str] = Field(default_factory=list)
    escudos: bool = False


class Dnd5eXpNivelItem(BaseModel):
    nivel: int = Field(ge=1, le=20)
    xp_total: int = Field(ge=0)


class Dnd5eRegrasClassesResponse(BaseModel):
    classes: List[Dnd5eClasseItem]
    xp_por_nivel: List[Dnd5eXpNivelItem]
    niveis_ganho_feat: List[int] = Field(default_factory=list)


class Dnd5eCondicaoItem(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=80)


class Dnd5eRegrasCombateResponse(BaseModel):
    formula_iniciativa: str
    formula_ataque: str
    formula_dano: str
    critico_em: int = Field(ge=1, le=30)
    rodada_segundos: int = Field(ge=1, le=60)
    condicoes: List[Dnd5eCondicaoItem]
    tipos_dano: List[str]
    acoes_turno: List[str]
    salvamentos_morte: Dict[str, int]


class Dnd5eMagiaCatalogoItem(BaseModel):
    slug: str = Field(..., max_length=80)
    nome: str = Field(..., max_length=120)
    nivel: int = Field(ge=0, le=9)
    escola: str = Field(default="", max_length=40)
    tempo_execucao: str = Field(default="acao", max_length=40)
    alcance: str = Field(default="", max_length=80)
    teste_resistencia: str = Field(default="nenhum", max_length=20)
    requer_concentracao: bool = False


class Dnd5eRegrasMagiasResponse(BaseModel):
    magias: List[Dnd5eMagiaCatalogoItem]
    conjuracao: Dict[str, Any] = Field(default_factory=dict)
    total: int = Field(ge=0)


class Dnd5eFeatCatalogoItem(BaseModel):
    slug: str = Field(..., max_length=80)
    nome: str = Field(..., max_length=120)
    tipo_bonus: str = Field(default="Utilidade", max_length=40)
    requisito_nivel: int = Field(default=1, ge=1, le=20)
    requisitos: Any = Field(default_factory=list)
    bonus_especial: Optional[Dict[str, Any]] = None


class Dnd5eRegrasTalentosResponse(BaseModel):
    talentos: List[Dnd5eFeatCatalogoItem]
    niveis_ganho_feat: List[int] = Field(default_factory=list)
    total: int = Field(ge=0)


class Dnd5eRegrasEquipamentoResponse(BaseModel):
    armas_simples: List[Dict[str, Any]]
    armas_marciais: List[Dict[str, Any]]
    armaduras: List[Dict[str, Any]]
    escudos: List[Dict[str, Any]]
    itens_variados: List[Dict[str, Any]] = Field(default_factory=list)


class Dnd5eAntecedenteCatalogoItem(BaseModel):
    slug: str = Field(..., max_length=80)
    nome: str = Field(..., max_length=120)
    pericias: List[str] = Field(default_factory=list)
    idiomas_qtd: int = Field(default=0, ge=0, le=10)
    equipamento: List[str] = Field(default_factory=list)
    ouro_extra: int = Field(default=0, ge=0)


class Dnd5eRegrasAntecedentesResponse(BaseModel):
    antecedentes: List[Dnd5eAntecedenteCatalogoItem]
    total: int = Field(ge=0)


class Dnd5ePericiaCatalogoItem(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=80)
    habilidade: str = Field(..., max_length=20)


class Dnd5eRegrasPericiasResponse(BaseModel):
    pericias: List[Dnd5ePericiaCatalogoItem]


class Dnd5eSubclasseItem(BaseModel):
    slug: str = Field(..., max_length=80)
    nome: str = Field(..., max_length=120)
    classe_slug: str = Field(..., max_length=40)
    nivel_escolha: int = Field(ge=1, le=20)


class Dnd5eRegrasSubclassesResponse(BaseModel):
    subclasses: List[Dnd5eSubclasseItem]


class Dnd5ePericiaGradeItem(BaseModel):
    slug: str
    nome: str
    habilidade: str
    proficiente: bool
    bonus: int


class Dnd5eSalvamentoItem(BaseModel):
    habilidade: str
    proficiente: bool
    bonus: int


class Dnd5eAntecedenteResumoItem(BaseModel):
    slug: str
    nome: str
    pericias: List[str] = Field(default_factory=list)
    idiomas_qtd: int = 0
    equipamento: List[str] = Field(default_factory=list)
    ouro_po: int = 0


class Dnd5eCalcularAtributosRequest(BaseModel):
    raca_slug: str = Field(..., max_length=40)
    classe_slug: str = Field(..., max_length=40)
    antecedente_slug: Optional[str] = Field(None, max_length=80)
    scores_base: Dict[str, int] = Field(default_factory=dict)
    bonus_habilidade_extra: Dict[str, int] = Field(default_factory=dict)
    bonus_atributo_feat: Dict[str, int] = Field(default_factory=dict)
    nivel: int = Field(default=1, ge=1, le=20)
    pericias_classe_escolhidas: List[str] = Field(default_factory=list)
    pericia_racial_extra: Optional[str] = Field(None, max_length=40)
    subclasse_slug: Optional[str] = Field(None, max_length=80)
    armadura_slug: Optional[str] = Field(None, max_length=80)
    escudo_slug: Optional[str] = Field(None, max_length=80)
    feats: List[str] = Field(default_factory=list)
    progressao: Optional[Dict[str, Any]] = None
    hp_roll_nivel_1: Optional[int] = Field(
        default=None,
        ge=1,
        le=12,
        description="Rolagem do dado de vida no nível 1; omitir usa o máximo da classe",
    )


class Dnd5eCalcularAtributosResponse(BaseModel):
    raca: Dict[str, str]
    classe: Dict[str, Any]
    subclasse: Optional[Dict[str, str]] = None
    antecedente: Optional[Dnd5eAntecedenteResumoItem] = None
    antecedente_slug: Optional[str] = None
    scores_base: Dict[str, int]
    scores_efetivos: Dict[str, int]
    modificadores: Dict[str, int]
    hp_max_nivel_1: int = Field(ge=1)
    hp_max_total: int = Field(default=0, ge=0)
    hp_resumo: Optional[Dict[str, Any]] = None
    feats: List[str] = Field(default_factory=list)
    pendencias: List[str] = Field(default_factory=list)
    ca_base: int = Field(ge=0)
    ca_total: int = Field(ge=0)
    armadura_slug: Optional[str] = None
    escudo_slug: Optional[str] = None
    iniciativa: int
    velocidade_metros: float = Field(ge=0)
    tracos_resumo: str = Field(default="", max_length=4000)
    bonus_proficiencia: int = Field(ge=2, le=6)
    nivel: int = Field(ge=1, le=20)
    pericias_proficientes: List[str] = Field(default_factory=list)
    pericias: List[Dnd5ePericiaGradeItem] = Field(default_factory=list)
    salvamentos: List[Dnd5eSalvamentoItem] = Field(default_factory=list)


class Dnd5eInventarioItemPayload(BaseModel):
    slug: str = Field(..., min_length=1, max_length=80)
    quantidade: int = Field(default=1, ge=1, le=999)


class Dnd5eCalcularEquipamentoRequest(BaseModel):
    armadura_slug: Optional[str] = Field(None, max_length=80)
    escudo_slug: Optional[str] = Field(None, max_length=80)
    arma_principal_slug: Optional[str] = Field(None, max_length=80)
    armas_slugs: List[str] = Field(default_factory=list)
    itens: List[Dnd5eInventarioItemPayload] = Field(default_factory=list)
    forca: int = Field(default=10, ge=1, le=30)
    dex_mod: int = Field(default=0, ge=-5, le=10)
    ouro_po: float = Field(default=0, ge=0)


class Dnd5eCalcularEquipamentoResponse(BaseModel):
    ca_total: int = Field(ge=0)
    armadura_slug: Optional[str] = None
    escudo_slug: Optional[str] = None
    arma_principal_slug: Optional[str] = None
    arma_principal: Optional[Dict[str, Any]] = None
    armas: List[Dict[str, Any]] = Field(default_factory=list)
    itens: List[Dict[str, Any]] = Field(default_factory=list)
    ouro_po: float = Field(default=0, ge=0)
    peso_total_lb: float = Field(ge=0)
    capacidade_lb: float = Field(ge=0)
    penalidade_velocidade_m: int = Field(ge=0)
    sobrecarregado: bool = False
