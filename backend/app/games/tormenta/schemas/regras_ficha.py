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


class TormentaDivindadeMbOpcao(BaseModel):
    """Uma divindade do MB: `slug` para motor/regras futuras; `rotulo` é o valor persistido em `divindade`."""

    slug: str = Field(..., max_length=40, description="Chave estável (ex.: valkaria, khalmyr).")
    rotulo: str = Field(..., max_length=120, description="Texto canónico no combo e no banco (`divindade`).")


class TormentaRegrasIdentidadeMbResponse(BaseModel):
    """Tendências (alinhamento) e divindades (Os Vinte) conforme MB — listas para `<select>` na ficha."""

    tendencias: List[str] = Field(
        default_factory=list,
        description="Grade de alinhamento MB (Cap. tendência; páginas ~116–119).",
    )
    divindades: List[TormentaDivindadeMbOpcao] = Field(
        default_factory=list,
        description="Panteão maior MB — Os Vinte (~p.120–126); cada item com slug + rótulo.",
    )


class TormentaCatalogoItem(BaseModel):
    """Item do catálogo MB (equipamentos ou talentos — campos de combate opcionais)."""

    id: int = Field(..., ge=1, description="Identificador estável após carregar o JSON (1..N).")
    nome: str = Field(..., max_length=200)
    categoria: Optional[str] = Field(
        default=None,
        max_length=80,
        description="Categoria opcional (ex.: arma, armadura, Geral, Combate).",
    )
    secao: Optional[str] = Field(
        default=None,
        max_length=200,
        description="Subtítulo / seção (ex.: Armas simples · Corpo a corpo; Resistência).",
    )
    prerequisitos: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Pré-requisitos do talento (catálogo de talentos MB).",
    )
    descricao_resumo: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Texto curto para lista / modal (talentos MB).",
    )
    pagina_referencia: Optional[str] = Field(
        default=None,
        max_length=80,
        description="Referência de página no MB (talentos).",
    )
    custo: Optional[str] = Field(default=None, max_length=80)
    dano_p: Optional[str] = Field(default=None, max_length=40)
    dano_m: Optional[str] = Field(default=None, max_length=40)
    tipo_dano: Optional[str] = Field(default=None, max_length=120)
    critico: Optional[str] = Field(default=None, max_length=80)
    alcance: Optional[str] = Field(default=None, max_length=80)
    peso: Optional[str] = Field(default=None, max_length=80)


class TormentaCatalogoPaginaResponse(BaseModel):
    itens: List[TormentaCatalogoItem]
    total: int = Field(..., ge=0, description="Total após filtro de busca (antes da paginação).")


class TormentaArmaduraCatalogoItem(BaseModel):
    """Item do catálogo de armadura / proteção (Tormenta 20 — livro base)."""

    id: int = Field(..., ge=1, description="Identificador estável após filtro (1..N).")
    nome: str = Field(..., max_length=200)
    tipo: str = Field(default="", max_length=120)
    bonus_ca: int = Field(default=0, ge=-20, le=30)
    penalidade: int = Field(default=0, ge=-20, le=20)
    des_max: Optional[str] = Field(default=None, max_length=40)
    falha_arcana: Optional[str] = Field(default=None, max_length=80)
    deslocamento: Optional[str] = Field(default=None, max_length=80)
    peso: Optional[str] = Field(default=None, max_length=40, description="Texto livre (ex.: 15 kg).")
    propriedades_especiais: Optional[str] = Field(default=None, max_length=2000)


class TormentaArmaduraCatalogoPaginaResponse(BaseModel):
    itens: List[TormentaArmaduraCatalogoItem]
    total: int = Field(..., ge=0, description="Total após filtro de busca (antes da paginação).")


class TormentaMagiaMbCatalogoItem(BaseModel):
    """Metadado de magia MB para grimório / listagens (sem texto integral do livro)."""

    id: int = Field(..., ge=1, description="Índice estável na lista filtrada ordenada (1..N).")
    slug: str = Field(..., max_length=80, description="Chave estável para vínculos e API.")
    nome: str = Field(..., max_length=200)
    circulo: int = Field(..., ge=0, le=20, description="0 = truque; 1+ = círculo da magia (MB).")
    tipo: Literal["arcana", "divina"] = Field(
        ...,
        description="Arcana ou divina (MB — tipos de magia).",
    )
    escola: Optional[str] = Field(default=None, max_length=80)
    resistencia: Optional[str] = Field(default=None, max_length=120)
    execucao: Optional[str] = Field(default=None, max_length=120)
    alcance: Optional[str] = Field(default=None, max_length=120)
    alvo: Optional[str] = Field(default=None, max_length=200)
    duracao: Optional[str] = Field(default=None, max_length=120)
    descricao_curta: Optional[str] = Field(
        default=None,
        max_length=500,
        description="Resumo curto; não substitui o texto do livro.",
    )
    descricao_longa: Optional[str] = Field(
        default=None,
        max_length=50_000,
        description="Reservado no contrato da API; não preenchido no catálogo (texto integral do livro).",
    )
    pagina_referencia: Optional[str] = Field(default=None, max_length=80)


class TormentaMagiaMbCatalogoPaginaResponse(BaseModel):
    itens: List[TormentaMagiaMbCatalogoItem]
    total: int = Field(..., ge=0, description="Total após filtros (antes da paginação).")


class TormentaConjuracaoClasseMbItem(BaseModel):
    """Progressão de PM e chave de conjuração por classe (MB)."""

    slug: str = Field(..., max_length=40)
    habilidade_chave: Literal["int", "sab", "car"] = Field(
        ...,
        description="Atributo que define CD e modificador na conjuração (MB).",
    )
    pm_constante: int = Field(..., ge=0, le=30)
    pm_por_nivel: int = Field(..., ge=0, le=10, description="PM adicionados por nível de classe (após o 1º ou após o nível de início).")
    conjuracao_inicia_nivel: int = Field(
        ...,
        ge=1,
        le=20,
        description="Nível mínimo da classe em que há conjuração (ex.: 5 para paladino/ranger com magias).",
    )


class TormentaConjuracaoCustoCirculoItem(BaseModel):
    circulo: int = Field(..., ge=0, le=20)
    custo_pm: int = Field(..., ge=0, le=30)


class TormentaRegrasConjuracaoMbResponse(BaseModel):
    """Tabelas de referência para Pontos de Magia (PM) e custo por círculo (grimório / ficha)."""

    classes: List[TormentaConjuracaoClasseMbItem]
    custo_pm_circulos: List[TormentaConjuracaoCustoCirculoItem]
    nota_custo_magia: str = Field(default="", max_length=500)


class TormentaConjuracaoPreviewResponse(BaseModel):
    """Pré-visualização de CD base, modificador da chave e PM máx. de conjuração MB (ficha atual)."""

    classe_slug: str = Field(..., max_length=40)
    nivel_conjuracao: int = Field(..., ge=1, le=40, description="Nível usado no cálculo (query ou padrão).")
    habilidade_chave: Optional[Literal["int", "sab", "car"]] = Field(
        default=None,
        description="Chave MB da classe; null se a classe não conjura no catálogo.",
    )
    modificador_conjuracao: Optional[int] = Field(
        default=None,
        ge=-99,
        le=99,
        description="Modificador do atributo-chave; null se não aplicável.",
    )
    cd_magia: Optional[int] = Field(
        default=None,
        ge=-99,
        le=99,
        description="CD base de magias (10 + modificador da chave, MB).",
    )
    pontos_magia_maximos: Optional[int] = Field(
        default=None,
        ge=0,
        le=9999,
        description="Pontos de Magia (PM) máximos MB no nível indicado; null se nível/classe não conjura.",
    )
    pontos_mana_maximos: Optional[int] = Field(
        default=None,
        ge=0,
        le=9999,
        description="Alias legado (nome ‘mana’); igual a pontos_magia_maximos.",
    )
    magias_lista_tipo: Optional[Literal["arcana", "divina"]] = Field(
        default=None,
        description="Tipo de magias do catálogo MB para a classe; null se não houver lista conjurador MB.",
    )
    magias_circulo_max: Optional[int] = Field(
        default=None,
        ge=0,
        le=9,
        description="Maior círculo lançável neste nível (0 = só truques); null se a classe não usa lista MB.",
    )
