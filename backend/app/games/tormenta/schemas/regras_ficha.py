"""Schemas — payload público de regras da ficha Tormenta 20."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class TormentaCustoAtributoItem(BaseModel):
    valor: int = Field(ge=-5, le=99)
    custo: int


class TormentaPericiaAtributoItem(BaseModel):
    slug: Optional[str] = Field(default=None, max_length=40)
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
    penalidade_armadura_natacao: Optional[bool] = Field(
        default=None,
        description="v1.3 Atletismo: penalidade só em natação (p.116).",
    )


class TormentaRegrasAtributosResponse(BaseModel):
    regra_versao: str = Field(default="mb", max_length=8)
    pontos_compra_iniciais: int = Field(default=20, ge=0, le=999)
    custos: List[TormentaCustoAtributoItem]
    pericias: List[TormentaPericiaAtributoItem]
    metodos_geracao: List[str] = Field(
        default_factory=lambda: ["compra_pontos", "4d6"],
        description="Métodos MB suportados na criação de personagem jogador.",
    )


class TormentaGerarAtributosRequest(BaseModel):
    metodo: Literal["compra_pontos", "4d6"] = Field(
        default="4d6",
        description="compra_pontos devolve base 0 (v1.3) ou 10 (MB); 4d6 rola/converte seis valores.",
    )
    regra_versao: Optional[str] = Field(
        default=None,
        description="Edição: mb ou v13. Padrão mb.",
        max_length=8,
    )
    seed: Optional[int] = Field(
        default=None,
        description="Semente opcional para reproduzir a mesma rolagem (testes/depuração).",
    )


class TormentaGerarAtributosResponse(BaseModel):
    metodo: Literal["compra_pontos", "4d6"]
    regra_versao: str = Field(default="mb", max_length=8)
    valores: Dict[str, int] = Field(
        description="Valores-base por atributo (for, des, con, int, sab, car), sem bônus racial.",
    )
    qualidade_4d6_ok: Optional[bool] = Field(
        default=None,
        description="Para 4d6: True se cumpre reroll MB (+4 mods ou algum 14+).",
    )
    soma_modificadores: Optional[int] = Field(
        default=None,
        description="Soma dos modificadores T20 dos seis valores-base.",
    )


class TormentaRacaMbItem(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=120)
    fonte_catalogo: str = Field(
        default="core",
        description="core = Módulo Básico / v1.3; herois_arton = suplemento Heróis de Arton.",
    )
    ajustes: Dict[str, int] = Field(default_factory=dict)
    escolhe_duas_mais2: bool = False
    escolhe_tres_mais1: bool = Field(
        default=False,
        description="v1.3: +1 em três atributos diferentes (humano, lefou, osteon, sereia).",
    )
    escolhe_um_mais2: bool = Field(
        default=False,
        description="Meio-orc: +2 em outra habilidade (excl. listadas em excluir_atributos_mais2).",
    )
    excluir_atributos_mais2: List[str] = Field(
        default_factory=list,
        description="Chaves for,des,con,int,sab,car excluídas do +2 opcional (ex.: int,car para meio-orc).",
    )
    excluir_atributos_mais1: List[str] = Field(default_factory=list)
    escolhe_suraggel_subtipo: bool = False
    escolhe_lefou_deformidade: bool = Field(
        default=False,
        description="v1.3: Lefou — Deformidade (+2 em 2 perícias ou 1 perícia + poder Tormenta).",
    )
    escolhe_qareen_ascendencia: bool = Field(
        default=False,
        description="v1.3: Qareen — ascendência elementar e magia 1º círculo.",
    )
    magias_inatas_v13: bool = Field(
        default=False,
        description="v1.3: raça concede magia(s) inata(s) fixas (ex.: Dahllan).",
    )
    escolhe_osteon_memoria: bool = Field(
        default=False,
        description="v1.3: Osteon — Memória Póstuma (perícia ou poder geral).",
    )
    escolhe_sereia_magias: bool = Field(
        default=False,
        description="v1.3: Sereia/Tritão — 2 magias da Canção dos Mares.",
    )
    escolhe_golem_fonte: bool = Field(
        default=False,
        description="v1.3: Golem — Fonte Elemental + poder geral.",
    )
    escolhe_kliren_hibrido: bool = Field(
        default=False,
        description="v1.3: Kliren — perícia Híbrido + Ofício Vanguardista.",
    )
    escolhe_silfide_magias: bool = Field(
        default=False,
        description="v1.3: Sílfide — 2 magias das Fadas.",
    )
    escolhe_um_mais1: bool = Field(
        default=False,
        description="Heróis de Arton: +1 em um atributo livre (ex.: Galokk).",
    )
    escolhe_dois_mais1: bool = Field(
        default=False,
        description="Heróis de Arton: +1 em dois atributos livres (ex.: Meio-Elfo, exceto Con).",
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
    regra_versao: str = Field(default="mb", max_length=8)
    racas: List[TormentaRacaMbItem]
    idiomas_geral_mb: str = Field(
        default="",
        max_length=12000,
        description="Regra geral de idiomas e alfabetização (MB).",
    )
    idiomas_tabela_mb: List[TormentaIdiomaTabelaItem] = Field(default_factory=list)


class TormentaBeneficioNivelMbItem(BaseModel):
    nivel: int = Field(..., ge=1, le=40)
    xp_total: int = Field(
        ..., ge=0, description="XP acumulado necessário para atingir este nível (MB)."
    )
    graduacao_pericias: str = Field(default="", max_length=40)
    talentos_totais: int = Field(
        default=1,
        ge=0,
        le=30,
        description="Total de talentos do personagem neste nível (MB).",
    )
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
    poderes_gerais_totais: Optional[int] = Field(
        default=None,
        ge=0,
        le=30,
        description="Total de poderes gerais (v1.3); espelha talentos_totais na API.",
    )


class TormentaClasseMbItem(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=80)
    abreviatura: str = Field(default="", max_length=8)
    fonte_catalogo: str = Field(
        default="core",
        description="core = classe base v1.3; herois_arton = suplemento Heróis de Arton.",
    )
    classe_variante_base: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Slug da classe base quando esta é uma variante (ex.: 'inventor' para 'alquimista').",
    )
    exclusivo_com: List[str] = Field(
        default_factory=list,
        description="Slugs de classes mutuamente exclusivas (variantes não podem ser usadas juntas).",
    )
    bba_tipo: Literal["plein", "tres_quartos", "meio"] = Field(
        default="plein",
        description="plein = BBA igual ao nível de classe; tres_quartos; meio (mago/feiticeiro).",
    )
    pv_inicial: int = Field(..., ge=1, le=99)
    pv_por_nivel: int = Field(..., ge=0, le=30)
    pm_por_nivel: Optional[int] = Field(
        default=None,
        ge=0,
        le=20,
        description="PM ganhos por nível na classe (v1.3 — Tabela 1-3).",
    )
    atributo_principal: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Atributo principal da classe (v1.3).",
    )
    pericias_treinadas: str = Field(default="", max_length=200)
    pericias_treinadas_base: Optional[int] = Field(
        default=None,
        ge=0,
        le=20,
        description="Vagas de perícia treinada da classe (antes do mod. INT e bônus racial).",
    )
    pericias_fixas: Optional[List[str]] = Field(
        default=None,
        description="Slugs de perícias treinadas fixas (v1.3).",
    )
    pericias_escolha_qtd: Optional[int] = Field(
        default=None,
        ge=0,
        le=20,
        description="Perícias à escolha da lista de classe (v1.3).",
    )
    pericias_escolha_de: Optional[List[str]] = Field(
        default=None,
        description="Pool de slugs para escolhas de classe (v1.3).",
    )
    pericias_escolha_um_de: Optional[List[List[str]]] = Field(
        default=None,
        description="Grupos «ou» de perícias de classe (v1.3), ex.: [[luta, pontaria]].",
    )
    vagas_classe: Optional[int] = Field(
        default=None,
        ge=0,
        le=30,
        description="Fixas + grupos «ou» + escolhas (v1.3).",
    )
    pericias_classe: str = Field(default="", max_length=2000)
    talentos_adicionais: str = Field(default="", max_length=2000)
    habilidades_por_nivel: Dict[str, str] = Field(
        default_factory=dict,
        description='Chaves "1".."20": texto MB deste nível (vazio = ver livro).',
    )


class TormentaRegrasClassesResponse(BaseModel):
    regra_versao: str = Field(default="mb", max_length=8)
    beneficios_por_nivel: List[TormentaBeneficioNivelMbItem]
    classes: List[TormentaClasseMbItem]


class TormentaObrigacaoFlagItem(BaseModel):
    slug: str = Field(..., max_length=60)
    rotulo: str = Field(..., max_length=120)


class TormentaDivindadeMbOpcao(BaseModel):
    """Uma divindade do MB: `slug` para motor/regras futuras; `rotulo` é o valor persistido em `divindade`."""

    slug: str = Field(
        ..., max_length=40, description="Chave estável (ex.: valkaria, khalmyr)."
    )
    rotulo: str = Field(
        ...,
        max_length=120,
        description="Texto canónico no combo e no banco (`divindade`).",
    )
    truque_devocao_slug: Optional[str] = Field(
        default=None,
        max_length=80,
        description="Prece de devoção (círculo 0) concedida a devotos — RF-T44d.",
    )
    energia: Optional[str] = Field(
        default=None,
        max_length=20,
        description="positiva | negativa | qualquer (v1.3).",
    )
    poderes_concedidos: List[str] = Field(
        default_factory=list,
        description="Slugs dos 4 poderes concedidos (Tabela 1-20 v1.3).",
    )
    pagina: Optional[int] = Field(
        default=None,
        ge=0,
        le=999,
        description="Página v1.3 com Obrigações & Restrições (Tabela 1-20).",
    )
    obrigacoes_flags: List[TormentaObrigacaoFlagItem] = Field(
        default_factory=list,
        description="Flags compactas de obrigações/restrições (RF-T09h).",
    )
    sem_penalidade_obrigacao: bool = Field(
        default=False,
        description="True se violar O&R não causa perda de PM (ex.: Nimb).",
    )


class TormentaOrigemV13Item(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=80)
    pagina: int = Field(default=0, ge=0, le=999)
    fonte_catalogo: str = Field(
        default="core",
        description="core = EJA v1.3; herois_arton = suplemento Heróis de Arton.",
    )
    beneficios_pericias: List[str] = Field(default_factory=list)
    beneficios_poderes: List[str] = Field(default_factory=list)
    poder_unico: Optional[str] = Field(default=None, max_length=60)
    itens: List[str] = Field(default_factory=list)
    itens_escolha: Optional[Dict[str, Any]] = Field(default=None)
    troca_pericia_treinada: bool = Field(
        default=False,
        description="Se perícia já treinada pode ser trocada por outra de classe (Heróis de Arton).",
    )
    notas: str = Field(default="", max_length=500)


class TormentaKitInicialV13Opcoes(BaseModel):
    fixos: List[str] = Field(default_factory=list)
    arma_simples: bool = True
    arma_marcial: bool = False
    armadura_leve: bool = True
    armadura_pesada_opcao: bool = False
    armaduras_leves: List[str] = Field(default_factory=list)
    armadura_pesada: str = "Brunea"
    escudo: bool = False
    sem_armadura: bool = False
    dinheiro_formula: str = "4d6"


class TormentaRegrasKitInicialV13Response(BaseModel):
    regra_versao: str = "v13"
    opcoes: TormentaKitInicialV13Opcoes


class TormentaRegrasOrigensResponse(BaseModel):
    regra_versao: str = "v13"
    origens: List[TormentaOrigemV13Item] = Field(default_factory=list)


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

    id: int = Field(
        ..., ge=1, description="Identificador estável após carregar o JSON (1..N)."
    )
    slug: Optional[str] = Field(
        default=None,
        max_length=80,
        description="Identificador estável do poder (suplemento Heróis de Arton).",
    )
    nome: str = Field(..., max_length=200)
    fonte_catalogo: Optional[str] = Field(
        default=None,
        max_length=40,
        description="core = Módulo Básico; herois_arton = suplemento Heróis de Arton.",
    )
    raca_exigida: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Raça exigida para poderes de raça (suplemento HA).",
    )
    classe_exigida: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Classe exigida para poderes de classe/treinador (suplemento HA).",
    )
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
    categoria_v13: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Categoria v1.3: geral, combate, destino, magia, concedido, tormenta, classe, raca, grupo, treinador, distincao.",
    )
    custo_pm: Optional[int] = Field(
        default=None,
        ge=0,
        le=99,
        description="PM gastos ao ativar o poder (0 = passivo ou desconhecido).",
    )
    pre_requisitos_v13: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Pré-requisitos estruturados v1.3 (RF-T08g).",
    )
    custo: Optional[str] = Field(default=None, max_length=80)
    dano_p: Optional[str] = Field(default=None, max_length=40)
    dano_m: Optional[str] = Field(default=None, max_length=40)
    tipo_dano: Optional[str] = Field(default=None, max_length=120)
    critico: Optional[str] = Field(default=None, max_length=80)
    alcance: Optional[str] = Field(default=None, max_length=80)
    peso: Optional[str] = Field(default=None, max_length=80)
    tipo: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Tipo v1.3 (leve, media, pesada, escudo) para armaduras.",
    )
    espacos: Optional[float] = Field(
        default=None,
        ge=0,
        le=100,
        description="Espaços de carga v1.3 (p.141).",
    )
    bonus_ca: Optional[int] = Field(default=None, ge=-20, le=30)
    penalidade: Optional[int] = Field(default=None, ge=-20, le=20)
    proficiencia: Optional[str] = Field(default=None, max_length=40)
    empunhadura: Optional[str] = Field(default=None, max_length=40)
    regra_versao: Optional[str] = Field(default=None, max_length=8)


class TormentaCatalogoPaginaResponse(BaseModel):
    itens: List[TormentaCatalogoItem]
    total: int = Field(
        ..., ge=0, description="Total após filtro de busca (antes da paginação)."
    )


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
    peso: Optional[str] = Field(
        default=None, max_length=40, description="Texto livre (ex.: 15 kg)."
    )
    propriedades_especiais: Optional[str] = Field(default=None, max_length=2000)


class TormentaArmaduraCatalogoPaginaResponse(BaseModel):
    itens: List[TormentaArmaduraCatalogoItem]
    total: int = Field(
        ..., ge=0, description="Total após filtro de busca (antes da paginação)."
    )


class TormentaMagiaMbCatalogoItem(BaseModel):
    """Metadado de magia MB para grimório / listagens (sem texto integral do livro)."""

    id: int = Field(
        ..., ge=1, description="Índice estável na lista filtrada ordenada (1..N)."
    )
    slug: str = Field(
        ..., max_length=80, description="Chave estável para vínculos e API."
    )
    nome: str = Field(..., max_length=200)
    circulo: int = Field(
        ..., ge=0, le=20, description="0 = truque; 1+ = círculo da magia (MB)."
    )
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
    total: int = Field(
        ..., ge=0, description="Total após filtros (antes da paginação)."
    )


class TormentaConjuracaoClasseMbItem(BaseModel):
    """Progressão de PM e chave de conjuração por classe (MB/v1.3)."""

    slug: str = Field(..., max_length=40)
    habilidade_chave: Literal["int", "sab", "car"] = Field(
        ...,
        description="Atributo que define CD e modificador na conjuração.",
    )
    pm_constante: int = Field(..., ge=0, le=30)
    pm_por_nivel: int = Field(
        ...,
        ge=0,
        le=10,
        description="PM adicionados por nível de classe (após o 1º ou após o nível de início).",
    )
    conjuracao_inicia_nivel: int = Field(
        ...,
        ge=1,
        le=20,
        description="Nível mínimo da classe em que há conjuração (ex.: 5 para paladino/ranger com magias).",
    )
    modo_conjuracao: Literal[
        "preparar", "espontaneo", "foco", "caminho", "nao_conjura"
    ] = Field(
        default="preparar",
        description="Tipo de conjuração por classe: preparar, espontâneo, foco, caminho (arcanista) ou não conjura.",
    )


class TormentaConjuracaoCustoCirculoItem(BaseModel):
    circulo: int = Field(..., ge=0, le=20)
    custo_pm: int = Field(..., ge=0, le=30)


class TormentaRegrasConjuracaoMbResponse(BaseModel):
    """Tabelas de referência para Pontos de Magia (PM) e custo por círculo (grimório / ficha)."""

    regra_versao: str = Field(default="mb", max_length=8)
    classes: List[TormentaConjuracaoClasseMbItem]
    custo_pm_circulos: List[TormentaConjuracaoCustoCirculoItem]
    nota_custo_magia: str = Field(default="", max_length=500)


class TormentaConjuracaoPreviewResponse(BaseModel):
    """Pré-visualização de CD base, modificador da chave e PM máx. de conjuração MB (ficha atual)."""

    classe_slug: str = Field(..., max_length=40)
    nivel_conjuracao: int = Field(
        ..., ge=1, le=40, description="Nível usado no cálculo (query ou padrão)."
    )
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


class TormentaTracosRaciaisPreviewResponse(BaseModel):
    slug: str
    encontrado: bool
    regra_versao: str = Field(default="mb", max_length=8)
    tamanho: Optional[str] = None
    deslocamento_m: Optional[int] = None
    tamanho_ui: Optional[str] = Field(
        None,
        max_length=8,
        description="Código UI: M, P, Min, G…",
    )
    tamanho_label: Optional[str] = Field(None, max_length=40)
    deslocamento_natacao_m: Optional[int] = Field(None, ge=0, le=999)
    deslocamento_voo_m: Optional[int] = Field(None, ge=0, le=999)
    deslocamento_pairar_m: Optional[int] = Field(None, ge=0, le=999)
    desloc_nao_reduz_armadura_carga: bool = Field(
        default=False,
        description="Anão/Golem: deslocamento não reduzido por armadura ou carga.",
    )
    ca_bonus: int = 0
    ca_vs_grande_ou_maior: int = 0
    ataque_bonus: int = 0
    furtividade_bonus: int = 0
    fortitude_bonus: int = 0
    reflexos_bonus: int = 0
    vontade_bonus: int = 0
    pericias_bonus: Dict[str, int] = Field(default_factory=dict)
    pericias_treinadas_extra: int = Field(default=0, ge=0, le=20)
    reducao_dano: Dict[str, int] = Field(
        default_factory=dict,
        description="RD por tipo de dano (escolhas raciais v1.3, ex.: qareen).",
    )
    imunidades_dano: Dict[str, bool] = Field(
        default_factory=dict,
        description="Imunidade a tipo de dano (escolhas raciais v1.3, ex.: golem).",
    )
    magias_inatas: List[str] = Field(
        default_factory=list,
        description="Slugs de magias inatas raciais (v1.3).",
    )
    escolhas_resumo: List[str] = Field(default_factory=list)
    pericias_treinadas_escolha: List[str] = Field(
        default_factory=list,
        description="Perícias marcadas treinadas por escolha racial (ex.: Osteon).",
    )


class TormentaEscolhaRacialFonteItem(BaseModel):
    slug: str = Field(..., max_length=40)
    rotulo: str = Field(..., max_length=80)
    imunidade_tipo: str = Field(..., max_length=40)


class TormentaEscolhaRacialMagiaOpcaoItem(BaseModel):
    slug: str = Field(..., max_length=80)
    nome: str = Field(..., max_length=120)


class TormentaEscolhaRacialModoItem(BaseModel):
    slug: str = Field(..., max_length=40)
    rotulo: str = Field(..., max_length=200)
    slots_pericia: int = Field(0, ge=0, le=5)
    slots_poder_tormenta: int = Field(0, ge=0, le=3)


class TormentaEscolhaRacialAscendenciaItem(BaseModel):
    slug: str = Field(..., max_length=40)
    rotulo: str = Field(..., max_length=80)
    rd_tipo: str = Field(..., max_length=40)
    rd_valor: int = Field(..., ge=0, le=99)


class TormentaEscolhaRacialMagiaInataItem(BaseModel):
    slug: str = Field(..., max_length=80)
    nome: str = Field(..., max_length=120)
    atributo_chave: str = Field(..., max_length=8)


class TormentaEscolhasRaciaisRacaResponse(BaseModel):
    slug: str = Field(..., max_length=40)
    tipo: str = Field(..., max_length=40)
    bonus_pericia: Optional[int] = Field(None, ge=0, le=20)
    categoria_poder: Optional[str] = Field(None, max_length=40)
    modos: Optional[List[TormentaEscolhaRacialModoItem]] = None
    ascendencias: Optional[List[TormentaEscolhaRacialAscendenciaItem]] = None
    magias_inatas: Optional[List[TormentaEscolhaRacialMagiaInataItem]] = None
    magia_circulo: Optional[int] = Field(None, ge=0, le=9)
    magia_lista: Optional[str] = Field(None, max_length=20)
    magia_atributo_chave: Optional[str] = Field(None, max_length=8)
    escolhas_qtd: Optional[int] = Field(None, ge=1, le=6)
    magias_opcoes: Optional[List[TormentaEscolhaRacialMagiaOpcaoItem]] = None
    fontes: Optional[List[TormentaEscolhaRacialFonteItem]] = None
    bonus_oficio: Optional[int] = Field(None, ge=0, le=20)
    slots_pericia: Optional[int] = Field(None, ge=0, le=5)


class TormentaEscolhasRaciaisResponse(BaseModel):
    regra_versao: str = Field(default="v13", max_length=8)
    raca: TormentaEscolhasRaciaisRacaResponse


class TormentaDificuldadePadraoItem(BaseModel):
    rotulo: str
    dc: int


class TormentaRegrasPericiasResponse(BaseModel):
    regra_versao: str = Field(default="mb", max_length=8)
    dificuldades: List[TormentaDificuldadePadraoItem]
    bonus_treinado: int = Field(
        default=2,
        description="MB: +2 fixo. v1.3: use bonus_treinamento_niveis.",
    )
    bonus_treinamento_niveis: Optional[List[Dict[str, int]]] = Field(
        default=None,
        description="v1.3: patamares 1–6 (+2), 7–14 (+4), 15+ (+6).",
    )


class TormentaPericiaBonusRequest(BaseModel):
    nivel: int = Field(1, ge=1, le=40)
    mod_atributo: int = Field(0, ge=-99, le=99)
    treinado: bool = False
    graduacao: int = Field(0, ge=0, le=99)
    outros: int = Field(0, ge=-99, le=99)
    racial_bonus: int = Field(0, ge=-99, le=99)
    penalidade_armadura: int = Field(
        0,
        ge=0,
        le=99,
        description="Override manual; ignorado se itens_protecao for enviado.",
    )
    pericia_de_classe: bool = False
    nome_pericia: Optional[str] = Field(None, max_length=120)
    slug_raca: Optional[str] = Field(None, max_length=40)
    regra_versao: Optional[str] = Field(
        default=None,
        max_length=8,
        description="mb ou v13 — altera fórmula de bônus e treino.",
    )
    itens_protecao: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Armaduras/escudos equipados — auto-calcula penalidade por perícia.",
    )
    uso_atletismo_natacao: bool = Field(
        default=False,
        description="Atletismo: penalidade só em natação (v1.3 p.116).",
    )
    penalidade_sobrecarga_carga: bool = Field(
        default=False,
        description="Sobrecarga de carga v1.3: +5 penalidade de armadura em perícias.",
    )
    tormenta_classe_mb_slug: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Slug da classe v1.3 — proficiência de armadura (RF-T07e-1).",
    )


class TormentaPericiaBonusResponse(BaseModel):
    bonus_total: int
    meio_nivel: int
    bonus_treinamento: int = Field(default=0, ge=0, le=10)
    penalidade_armadura_aplicada: int = Field(
        default=0,
        ge=0,
        le=99,
        description="Penalidade subtraída do bônus (armadura + escudo).",
    )
    percepcao_passiva: Optional[int] = None
    pode_usar: bool = Field(default=True)
    motivo_bloqueio: str = Field(default="", max_length=300)


class TormentaPericiaRolarRequest(BaseModel):
    bonus: int = Field(0, ge=-99, le=99)
    dc: int = Field(15, ge=0, le=99)


class TormentaPericiaRolarResponse(BaseModel):
    d20: int
    bonus: int
    total: int
    dc: int
    sucesso: bool
    falha_critica: bool
    sucesso_critico: bool
    margem: int


class TormentaAtaqueBonusRequest(BaseModel):
    bonus_base: int = Field(0, ge=-99, le=99)
    nome_arma: Optional[str] = Field(default=None, max_length=120)
    proficiencia_arma: Optional[str] = Field(default=None, max_length=40)
    tormenta_classe_mb_slug: Optional[str] = Field(default=None, max_length=40)


class TormentaAtaqueBonusResponse(BaseModel):
    bonus_base: int
    bonus_efetivo: int
    penalidade_nao_proficiente: int = Field(default=0, ge=0, le=5)
    proficiente: bool = True
    proficiencia_arma: str = Field(default="simples", max_length=40)


class TormentaCargaItemRef(BaseModel):
    nome: str = Field(default="", max_length=200)
    quantidade: int = Field(default=1, ge=1, le=9999)
    categoria: Optional[str] = Field(default=None, max_length=80)
    tipo: Optional[str] = Field(default=None, max_length=40)
    espacos: Optional[float] = Field(default=None, ge=0, le=100)


class TormentaCargaPreviewRequest(BaseModel):
    for_valor: int = Field(..., ge=-99, le=99)
    itens: List[TormentaCargaItemRef] = Field(default_factory=list)
    moedas_total: int = Field(default=0, ge=0, le=9_999_999)


class TormentaCargaDetalheItem(BaseModel):
    nome: str
    quantidade: int = 1
    espacos_unidade: float = 0
    espacos_total: float = 0


class TormentaCargaPreviewResponse(BaseModel):
    limite: int
    limite_maximo: int
    espacos_usados: float
    espacos_itens: float
    espacos_moedas: int
    estado: str = Field(description="normal | sobrecarregado | acima_maximo")
    sobrecarga: bool
    penalidade_armadura_extra: int = 0
    deslocamento_extra_m: int = 0
    detalhes: List[TormentaCargaDetalheItem] = Field(default_factory=list)


class TormentaMulticlasseClasseItem(BaseModel):
    slug: str = Field(..., min_length=1, max_length=40)
    nivel: int = Field(..., ge=1, le=40)


class TormentaPmMulticlasseLinha(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(default="", max_length=80)
    nivel: int = Field(..., ge=1, le=40)
    pm_por_nivel: Optional[int] = Field(default=None, ge=0, le=99)
    pm_classe: Optional[int] = Field(default=None, ge=0, le=9999)


class TormentaPmMulticlassePreviewRequest(BaseModel):
    classes: List[TormentaMulticlasseClasseItem] = Field(default_factory=list)
    regra_versao: Optional[str] = Field(default=None, max_length=8)


class TormentaPmMulticlassePreviewResponse(BaseModel):
    regra_versao: str = Field(default="v13", max_length=8)
    pm_max: Optional[int] = Field(default=None, ge=0, le=9999)
    breakdown: List[TormentaPmMulticlasseLinha] = Field(default_factory=list)
    formula: str = Field(default="", max_length=500)
    nivel_total_classes: int = Field(default=0, ge=0, le=800)


class TormentaDinheiroInicialResponse(BaseModel):
    regra_versao: str = Field(default="v13", max_length=8)
    nivel: int = Field(..., ge=1, le=40)
    tipo: str = Field(..., description="4d6 ou fixo", max_length=8)
    valor: Optional[int] = Field(default=None, ge=0, le=9999999)
    tabela_ref: str = Field(default="Tabela 3-1", max_length=32)


class TormentaPvPreviewResponse(BaseModel):
    classe_slug: str = Field(..., max_length=40)
    classe_nome: str = Field(default="", max_length=80)
    encontrado: bool = True
    regra_versao: str = Field(default="mb", max_length=8)
    nivel: int = Field(..., ge=1, le=40)
    pv_inicial: Optional[int] = Field(default=None, ge=1, le=99)
    pv_por_nivel: Optional[int] = Field(default=None, ge=0, le=30)
    mod_con: int = Field(default=0, ge=-99, le=99)
    contrib_niveis_extras: Optional[int] = Field(default=None, ge=0, le=999)
    contrib_constituicao: Optional[int] = Field(default=None, ge=-999, le=999)
    pv_max: Optional[int] = Field(default=None, ge=1, le=999)
    pm_por_nivel: Optional[int] = Field(default=None, ge=0, le=99)
    pm_max: Optional[int] = Field(default=None, ge=0, le=9999)


class TormentaPericiaFichaItem(BaseModel):
    nome: str = Field(default="", max_length=120)
    treinado: bool = False
    graduacao: int = Field(default=0, ge=0, le=99)
    total: Optional[int] = Field(default=None, ge=0, le=99)


class TormentaPericiasValidarCriacaoRequest(BaseModel):
    nivel: int = Field(1, ge=1, le=40)
    classe_slug: str = Field(..., min_length=1, max_length=40)
    int_valor: int = Field(10, ge=-99, le=99)
    slug_raca: Optional[str] = Field(None, max_length=40)
    pericias: List[TormentaPericiaFichaItem] = Field(default_factory=list)
    regra_versao: Optional[str] = Field(default=None, max_length=8)
    humano_versatil: Optional[str] = Field(
        default=None,
        max_length=32,
        description="Humano v1.3 Versátil: duas_pericias | pericia_poder",
    )
    origem_beneficios: Optional[List[str]] = Field(
        default=None,
        description="Benefícios de origem v1.3 (pericia:slug / poder:slug).",
    )
    origem_slug: Optional[str] = Field(
        default=None,
        max_length=40,
        description="Slug da origem v1.3 (necessário para trocas Heróis de Arton).",
    )
    origem_trocas_pericia: Optional[Dict[str, str]] = Field(
        default=None,
        description=(
            "Mapa perícia redundante → perícia de classe substituta "
            "(origens com troca_pericia_treinada)."
        ),
    )


class TormentaPericiasValidarCriacaoResponse(BaseModel):
    valido: bool
    motivo: str = Field(default="", max_length=500)
    regra_versao: str = Field(default="mb", max_length=8)
    vagas_treinadas: Optional[int] = Field(default=None, ge=0, le=99)
    usadas_treinadas: int = Field(default=0, ge=0, le=99)
    pontos_grad_treinadas: int = Field(default=0, ge=0, le=99)
    gasto_grad_treinadas: int = Field(default=0, ge=0, le=99)
    pontos_grad_nao_treinadas: int = Field(default=0, ge=0, le=99)
    gasto_grad_nao_treinadas: int = Field(default=0, ge=0, le=99)
    graduacao_pericias_texto: str = Field(default="", max_length=40)
    mod_int: int = Field(default=0, ge=-99, le=99)
    pericias_treinadas_extra_racial: int = Field(default=0, ge=0, le=20)
    pericias_treinadas_extra_origem: int = Field(default=0, ge=0, le=5)
    vagas_treinadas_base: Optional[int] = Field(default=None, ge=0, le=99)
    nivel: int = Field(default=1, ge=1, le=40)
    classe_slug: str = Field(default="", max_length=40)


class TormentaCondicaoV13Item(BaseModel):
    slug: str = Field(..., max_length=60)
    nome: str = Field(..., max_length=80)
    categoria: Optional[str] = Field(default=None, max_length=40)
    mod_ataque: Optional[int] = None
    mod_ca: Optional[int] = None
    efeito_resumo: Optional[str] = Field(default=None, max_length=400)


class TormentaCondicoesV13Response(BaseModel):
    condicoes: list[TormentaCondicaoV13Item]
    situacoes_especiais: list[TormentaCondicaoV13Item]
    total: int = Field(..., ge=0)


class TormentaPoderPreRequisitoFaltandoItem(BaseModel):
    tipo: str = Field(default="", max_length=40)
    descricao: str = Field(default="", max_length=200)


class TormentaPoderValidarPreRequisitosRequest(BaseModel):
    nome_poder: str = Field(..., min_length=2, max_length=200)
    regra_versao: Optional[str] = Field(default="v13", max_length=8)
    nivel: int = Field(default=1, ge=1, le=40)
    for_valor: int = Field(default=0, ge=-99, le=99)
    des_valor: int = Field(default=0, ge=-99, le=99)
    con_valor: int = Field(default=0, ge=-99, le=99)
    int_valor: int = Field(default=0, ge=-99, le=99)
    sab_valor: int = Field(default=0, ge=-99, le=99)
    car_valor: int = Field(default=0, ge=-99, le=99)
    ficha_json: Optional[Dict[str, Any]] = Field(default=None)
    poderes_escolhidos: List[str] = Field(default_factory=list)


class TormentaPoderValidarPreRequisitosResponse(BaseModel):
    valido: bool
    nome_poder: str = Field(..., max_length=200)
    faltando: List[TormentaPoderPreRequisitoFaltandoItem] = Field(default_factory=list)
    pre_requisitos: List[Dict[str, Any]] = Field(default_factory=list)
    motivo: str = Field(default="", max_length=500)


# ---------------------------------------------------------------------------
# Heróis de Arton — Melhor Amigo (Treinador)
# ---------------------------------------------------------------------------


class TormentaTruqueMelhorAmigoItem(BaseModel):
    slug: str = Field(..., max_length=60)
    nome: str = Field(..., max_length=120)
    descricao: str = Field(default="", max_length=2000)
    nivel_minimo: int = Field(default=1, ge=1, le=20)
    pre_requisito: Optional[str] = Field(default=None, max_length=60)


class TormentaTruquesMelhorAmigoResponse(BaseModel):
    nivel_treinador: int = Field(default=1, ge=1, le=20)
    qtd_maxima_truques: int = Field(default=2)
    truques: List[TormentaTruqueMelhorAmigoItem] = Field(default_factory=list)


class TormentaTipoMelhorAmigoItem(BaseModel):
    slug: str = Field(..., max_length=40)
    nome: str = Field(..., max_length=80)
    descricao: str = Field(default="", max_length=2000)
    bonus_atributos: Dict[str, int] = Field(default_factory=dict)
    sentidos: List[str] = Field(default_factory=list)
    imunidades: List[str] = Field(default_factory=list)
    bonus_pericias: Dict[str, int] = Field(default_factory=dict)
    rd_bonus: int = Field(default=0, ge=0)
    margem_ameaca_bonus: int = Field(default=0, ge=0)
    notas: str = Field(default="", max_length=1000)


class TormentaTiposMelhorAmigoResponse(BaseModel):
    tipos: List[TormentaTipoMelhorAmigoItem] = Field(default_factory=list)
