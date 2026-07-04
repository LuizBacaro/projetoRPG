"""HTTP — regras de ficha Tormenta 20 (dados estáticos para o frontend)."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.games.tormenta.rules.atributos_t20 import (
    CHAVES_ATRIBUTO,
    METODOS_GERACAO_ATRIBUTOS,
    gerar_seis_valores_4d6,
    lista_custos_compra,
    lista_pericias_com_atributo,
    pontos_iniciais_compra,
    qualidade_geracao_4d6,
    qualidade_geracao_4d6_v13,
    soma_modificadores_valores,
    valor_base_inicial_compra,
    valores_4d6_para_mapa,
)
from app.games.tormenta.rules.beneficios_nivel_t20 import lista_beneficios_por_nivel
from app.games.tormenta.rules.carga_t20 import PENALIDADE_SOBRECARGA, preview_carga_v13
from app.games.tormenta.rules.catalogo_armaduras_t20 import (
    filtrar_armaduras_protecao_mb,
)
from app.games.tormenta.rules.catalogo_t20 import (
    filtrar_equipamentos_mb,
    filtrar_magias_mb,
    filtrar_talentos_mb,
)
from app.games.tormenta.rules.classes_t20 import (
    lista_classes,
    lista_classes_com_suplemento,
)
from app.games.tormenta.rules.condicoes_t20 import (
    lista_condicoes_v13,
    lista_situacoes_especiais_v13,
)
from app.games.tormenta.rules.conjuracao_t20 import (
    cd_resistencia_magia_t20,
    custo_pm_preparar_ou_lancar_magia,
    habilidade_chave_conjuracao,
    lista_regras_conjuracao_por_versao,
    modificador_conjuracao_mb,
    pontos_magia_maximos_conjuracao,
    texto_custo_pm_por_circulo_mb,
)
from app.games.tormenta.rules.devocao_divindade_t20 import (
    truque_devocao_por_divindade_mb,
)
from app.games.tormenta.rules.dinheiro_inicial_v13_t20 import (
    preview_dinheiro_inicial_v13,
)
from app.games.tormenta.rules.escolhas_raciais_t20 import escolhas_por_raca
from app.games.tormenta.rules.kit_inicial_v13_t20 import opcoes_kit_inicial_v13
from app.games.tormenta.rules.magias_progressao_mb_t20 import (
    circulo_maximo_magias_lancaveis_mb,
    tipo_lista_magias_por_classe_mb,
)
from app.games.tormenta.rules.melhor_amigo_t20 import (
    lista_tipos_melhor_amigo,
    qtd_truques_por_nivel,
    truques_disponiveis,
)
from app.games.tormenta.rules.origens_t20 import lista_origens_com_suplemento
from app.games.tormenta.rules.penalidade_armadura_t20 import (
    penalidade_armadura_pericia,
    pericia_aplica_penalidade_armadura,
)
from app.games.tormenta.rules.pericias_classe_t20 import preview_pericias_classe_v13
from app.games.tormenta.rules.pericias_criacao_t20 import preview_pericias_criacao
from app.games.tormenta.rules.pericias_t20 import (
    bonus_treinamento_por_nivel,
    calcular_bonus_pericia,
    lista_dificuldades_padrao_mb,
    meta_pericia_por_nome,
    percepcao_passiva_t20,
    pode_usar_pericia_treinada,
    racial_bonus_pericia,
    rolar_teste_pericia,
)
from app.games.tormenta.rules.proficiencia_arma_t20 import ajustar_bonus_ataque_v13
from app.games.tormenta.rules.proficiencia_armadura_t20 import (
    tem_protecao_sem_proficiencia,
)
from app.games.tormenta.rules.progressao_pv_t20 import (
    preview_pm_multiclasse_v13,
    preview_pv_mb,
)
from app.games.tormenta.rules.racas_t20 import (
    idiomas_mb_extras,
    lista_racas_com_suplemento,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    SUPLEMENTO_HEROIS_ARTON,
    normalizar_regra_versao,
)
from app.games.tormenta.rules.tendencias_divindades_t20 import (
    lista_divindades_mb,
    lista_tendencias_mb,
)
from app.games.tormenta.rules.tracos_raciais_t20 import preview_tracos_raciais
from app.games.tormenta.schemas.regras_ficha import (
    TormentaArmaduraCatalogoItem,
    TormentaArmaduraCatalogoPaginaResponse,
    TormentaAtaqueBonusRequest,
    TormentaAtaqueBonusResponse,
    TormentaBeneficioNivelMbItem,
    TormentaCargaDetalheItem,
    TormentaCargaPreviewRequest,
    TormentaCargaPreviewResponse,
    TormentaCatalogoItem,
    TormentaCatalogoPaginaResponse,
    TormentaClasseMbItem,
    TormentaCondicaoV13Item,
    TormentaCondicoesV13Response,
    TormentaConjuracaoClasseMbItem,
    TormentaConjuracaoCustoCirculoItem,
    TormentaConjuracaoPreviewResponse,
    TormentaCustoAtributoItem,
    TormentaDinheiroInicialResponse,
    TormentaDivindadeMbOpcao,
    TormentaEscolhaRacialAscendenciaItem,
    TormentaEscolhaRacialFonteItem,
    TormentaEscolhaRacialMagiaInataItem,
    TormentaEscolhaRacialMagiaOpcaoItem,
    TormentaEscolhaRacialModoItem,
    TormentaEscolhasRaciaisRacaResponse,
    TormentaEscolhasRaciaisResponse,
    TormentaGerarAtributosRequest,
    TormentaGerarAtributosResponse,
    TormentaIdiomaTabelaItem,
    TormentaKitInicialV13Opcoes,
    TormentaMagiaMbCatalogoItem,
    TormentaMagiaMbCatalogoPaginaResponse,
    TormentaOrigemV13Item,
    TormentaPericiaAtributoItem,
    TormentaPericiaBonusRequest,
    TormentaPericiaBonusResponse,
    TormentaPericiaRolarRequest,
    TormentaPericiaRolarResponse,
    TormentaPericiasValidarCriacaoRequest,
    TormentaPericiasValidarCriacaoResponse,
    TormentaPmMulticlassePreviewRequest,
    TormentaPmMulticlassePreviewResponse,
    TormentaPoderValidarPreRequisitosRequest,
    TormentaPoderValidarPreRequisitosResponse,
    TormentaPvPreviewResponse,
    TormentaRacaMbItem,
    TormentaRegrasAtributosResponse,
    TormentaRegrasClassesResponse,
    TormentaRegrasConjuracaoMbResponse,
    TormentaRegrasIdentidadeMbResponse,
    TormentaRegrasKitInicialV13Response,
    TormentaRegrasOrigensResponse,
    TormentaRegrasPericiasResponse,
    TormentaRegrasRacasResponse,
    TormentaTipoMelhorAmigoItem,
    TormentaTiposMelhorAmigoResponse,
    TormentaTracosRaciaisPreviewResponse,
    TormentaTruqueMelhorAmigoItem,
    TormentaTruquesMelhorAmigoResponse,
)
from app.games.tormenta.services.personagem_talentos_service import (
    TormentaPersonagemTalentosService,
)
from app.shared.core.deps import get_usuario_atual, requer_game_tormenta
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/tormenta/regras",
    tags=["Tormenta — Regras"],
    dependencies=[Depends(requer_game_tormenta)],
)


@router.get(
    "/atributos",
    response_model=TormentaRegrasAtributosResponse,
    summary="Custos de compra por pontos e perícias com atributo-chave",
)
def obter_regras_atributos(
    regra_versao: Optional[str] = Query(
        None,
        description="Edição: mb (legado) ou v13 (Jogo do Ano). Padrão mb.",
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasAtributosResponse:
    rv = normalizar_regra_versao(regra_versao)
    custos = [TormentaCustoAtributoItem(**row) for row in lista_custos_compra(rv)]
    pericias = [
        TormentaPericiaAtributoItem(**row) for row in lista_pericias_com_atributo(rv)
    ]
    return TormentaRegrasAtributosResponse(
        regra_versao=rv,
        pontos_compra_iniciais=pontos_iniciais_compra(rv),
        custos=custos,
        pericias=pericias,
        metodos_geracao=sorted(METODOS_GERACAO_ATRIBUTOS),
    )


@router.post(
    "/gerar-atributos",
    response_model=TormentaGerarAtributosResponse,
    summary="Gera valores-base de atributos (compra por pontos ou 4d6 MB)",
)
def gerar_atributos(
    payload: TormentaGerarAtributosRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaGerarAtributosResponse:
    metodo = payload.metodo
    rv = normalizar_regra_versao(payload.regra_versao)
    if metodo == "compra_pontos":
        base = valor_base_inicial_compra(rv)
        valores = {chave: base for chave in CHAVES_ATRIBUTO}
        soma = soma_modificadores_valores(valores.values(), rv)
        return TormentaGerarAtributosResponse(
            metodo=metodo,
            regra_versao=rv,
            valores=valores,
            qualidade_4d6_ok=None,
            soma_modificadores=soma,
        )
    try:
        rolados = gerar_seis_valores_4d6(
            seed=payload.seed, exigir_qualidade_mb=True, regra_versao=rv
        )
        valores = valores_4d6_para_mapa(rolados)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    soma = soma_modificadores_valores(rolados, rv)
    q_ok = (
        qualidade_geracao_4d6_v13(rolados)
        if rv == "v13"
        else qualidade_geracao_4d6(rolados)
    )
    return TormentaGerarAtributosResponse(
        metodo=metodo,
        regra_versao=rv,
        valores=valores,
        qualidade_4d6_ok=q_ok,
        soma_modificadores=soma,
    )


@router.get(
    "/racas",
    response_model=TormentaRegrasRacasResponse,
    summary="Raças do Módulo Básico (ajustes, traços, idioma racial) + regra e tabela de idiomas MB",
)
def obter_regras_racas(
    regra_versao: Optional[str] = Query(
        None,
        description="Edição: mb (11 raças) ou v13 (17 raças). Padrão mb.",
    ),
    suplemento: Optional[str] = Query(
        None,
        description=(
            f"Incluir raças de suplemento: '{SUPLEMENTO_HEROIS_ARTON}' "
            "adiciona Eiradaan, Galokk, Meio-Elfo e Sátiro."
        ),
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasRacasResponse:
    rv = normalizar_regra_versao(regra_versao)
    geral, tabela = idiomas_mb_extras()
    racas_list = lista_racas_com_suplemento(rv, suplemento=suplemento)
    racas = [TormentaRacaMbItem(**row) for row in racas_list]
    idiomas_rows = [TormentaIdiomaTabelaItem(**row) for row in tabela]
    return TormentaRegrasRacasResponse(
        regra_versao=rv,
        racas=racas,
        idiomas_geral_mb=geral,
        idiomas_tabela_mb=idiomas_rows,
    )


@router.get(
    "/classes",
    response_model=TormentaRegrasClassesResponse,
    summary="Benefícios por nível e classes com BBA, PV, PM e perícias",
)
def obter_regras_classes(
    regra_versao: Optional[str] = Query(
        None,
        description="Versão de regras: mb (legado) ou v13 (Edição Jogo do Ano v1.3). Default: mb.",
    ),
    suplemento: Optional[str] = Query(
        None,
        description=(
            f"Incluir classes de suplemento: '{SUPLEMENTO_HEROIS_ARTON}' adiciona "
            "Treinador + 14 classes variantes."
        ),
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasClassesResponse:
    rv = normalizar_regra_versao(regra_versao)
    ben = [
        TormentaBeneficioNivelMbItem(**row) for row in lista_beneficios_por_nivel(rv)
    ]
    cls_rows = [
        TormentaClasseMbItem(**row)
        for row in lista_classes_com_suplemento(rv, suplemento)
    ]
    return TormentaRegrasClassesResponse(
        regra_versao=rv,
        beneficios_por_nivel=ben,
        classes=cls_rows,
    )


@router.get(
    "/identidade-mb",
    response_model=TormentaRegrasIdentidadeMbResponse,
    summary="Tendências (alinhamento) e divindades MB para combos na ficha",
)
def obter_regras_identidade_mb(
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasIdentidadeMbResponse:
    div_rows = []
    for row in lista_divindades_mb():
        slug = str(row.get("slug") or "").strip().lower()
        div_rows.append(
            TormentaDivindadeMbOpcao(
                slug=slug,
                rotulo=str(row.get("rotulo") or ""),
                truque_devocao_slug=truque_devocao_por_divindade_mb(slug),
                energia=row.get("energia"),
                poderes_concedidos=list(row.get("poderes_concedidos") or []),
                pagina=row.get("pagina"),
                obrigacoes_flags=list(row.get("obrigacoes_flags") or []),
                sem_penalidade_obrigacao=bool(row.get("sem_penalidade_obrigacao")),
            )
        )
    return TormentaRegrasIdentidadeMbResponse(
        tendencias=lista_tendencias_mb(),
        divindades=div_rows,
    )


@router.get(
    "/origens",
    response_model=TormentaRegrasOrigensResponse,
    summary="Origens v1.3 (Tabela 1-19) — benefícios de perícia e poder",
)
def obter_regras_origens(
    regra_versao: Optional[str] = Query(
        None,
        description="Versão de regras: v13 (padrão para origens).",
    ),
    suplemento: Optional[str] = Query(
        None,
        description=(
            f"Incluir origens de suplemento: '{SUPLEMENTO_HEROIS_ARTON}' adiciona "
            "14 origens especiais."
        ),
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasOrigensResponse:
    rv = normalizar_regra_versao(regra_versao or REGRA_VERSAO_V13)
    rows = [
        TormentaOrigemV13Item(**row) for row in lista_origens_com_suplemento(suplemento)
    ]
    return TormentaRegrasOrigensResponse(regra_versao=rv, origens=rows)


@router.get(
    "/truques-melhor-amigo",
    response_model=TormentaTruquesMelhorAmigoResponse,
    summary="Truques disponíveis para o Melhor Amigo do Treinador (Heróis de Arton)",
)
def obter_truques_melhor_amigo(
    nivel_treinador: int = Query(
        default=1,
        ge=1,
        le=20,
        description="Nível atual do Treinador para filtrar truques por nivel_minimo.",
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaTruquesMelhorAmigoResponse:
    truques = [
        TormentaTruqueMelhorAmigoItem(**t) for t in truques_disponiveis(nivel_treinador)
    ]
    return TormentaTruquesMelhorAmigoResponse(
        nivel_treinador=nivel_treinador,
        qtd_maxima_truques=qtd_truques_por_nivel(nivel_treinador),
        truques=truques,
    )


@router.get(
    "/tipos-melhor-amigo",
    response_model=TormentaTiposMelhorAmigoResponse,
    summary="Tipos de Melhor Amigo e bônus automáticos (Heróis de Arton)",
)
def obter_tipos_melhor_amigo(
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaTiposMelhorAmigoResponse:
    tipos = [TormentaTipoMelhorAmigoItem(**t) for t in lista_tipos_melhor_amigo()]
    return TormentaTiposMelhorAmigoResponse(tipos=tipos)


@router.get(
    "/kit-inicial",
    response_model=TormentaRegrasKitInicialV13Response,
    summary="Equipamento inicial v1.3 (p.140) — opções por classe",
)
def obter_regras_kit_inicial_v13(
    tormenta_classe_mb_slug: Optional[str] = Query(
        None,
        description="Slug da classe v1.3 para proficiências do kit.",
    ),
    regra_versao: Optional[str] = Query(None),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasKitInicialV13Response:
    rv = normalizar_regra_versao(regra_versao or REGRA_VERSAO_V13)
    slug = str(tormenta_classe_mb_slug or "").strip().lower()
    op = opcoes_kit_inicial_v13(slug)
    return TormentaRegrasKitInicialV13Response(
        regra_versao=rv,
        opcoes=TormentaKitInicialV13Opcoes(**op),
    )


@router.get(
    "/equipamentos",
    response_model=TormentaCatalogoPaginaResponse,
    summary="Catálogo MB de equipamento (busca e paginação)",
)
def listar_catalogo_equipamentos(
    q: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    response: Response = None,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaCatalogoPaginaResponse:
    slice_rows, total = filtrar_equipamentos_mb(q, skip, limit)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)
    itens = [TormentaCatalogoItem.model_validate(r) for r in slice_rows]
    return TormentaCatalogoPaginaResponse(itens=itens, total=total)


@router.get(
    "/talentos",
    response_model=TormentaCatalogoPaginaResponse,
    summary="Catálogo MB de talentos (agregado das classes + busca)",
)
@router.get(
    "/poderes",
    response_model=TormentaCatalogoPaginaResponse,
    summary="Alias v1.3 — catálogo de poderes (mesmo que /talentos)",
    include_in_schema=True,
)
def listar_catalogo_talentos(
    q: Optional[str] = None,
    categoria_v13: Optional[str] = Query(
        None,
        max_length=40,
        description="Filtrar por categoria v1.3 (geral, combate, destino, magia, concedido, tormenta, classe).",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    response: Response = None,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaCatalogoPaginaResponse:
    slice_rows, total = filtrar_talentos_mb(q, skip, limit, categoria_v13=categoria_v13)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)
    itens = [TormentaCatalogoItem.model_validate(r) for r in slice_rows]
    return TormentaCatalogoPaginaResponse(itens=itens, total=total)


@router.get(
    "/armaduras-protecao",
    response_model=TormentaArmaduraCatalogoPaginaResponse,
    summary="Catálogo de armaduras / itens de proteção (preenchível a partir do livro T20)",
)
def listar_catalogo_armaduras_protecao(
    q: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    response: Response = None,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaArmaduraCatalogoPaginaResponse:
    slice_rows, total = filtrar_armaduras_protecao_mb(q, skip, limit)
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)
    itens = [TormentaArmaduraCatalogoItem.model_validate(r) for r in slice_rows]
    return TormentaArmaduraCatalogoPaginaResponse(itens=itens, total=total)


@router.get(
    "/condicoes",
    response_model=TormentaCondicoesV13Response,
    summary="Catálogo de condições v1.3 (Apêndice B p.394) e situações especiais (Tabela 5-3)",
)
def listar_condicoes_v13(
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaCondicoesV13Response:
    cond = [TormentaCondicaoV13Item.model_validate(r) for r in lista_condicoes_v13()]
    sit = [
        TormentaCondicaoV13Item.model_validate(r)
        for r in lista_situacoes_especiais_v13()
    ]
    return TormentaCondicoesV13Response(
        condicoes=cond,
        situacoes_especiais=sit,
        total=len(cond) + len(sit),
    )


@router.get(
    "/magias",
    response_model=TormentaMagiaMbCatalogoPaginaResponse,
    summary="Catálogo MB de magias (metadados; busca e paginação)",
)
def listar_catalogo_magias(
    q: Optional[str] = None,
    circulo: Optional[int] = Query(
        None, ge=0, le=20, description="0 = truque; omitir para todos."
    ),
    tipo: Optional[str] = Query(None, description="arcana ou divina."),
    escola: Optional[str] = Query(
        None, description="Substring na escola (ex.: Abjuração)."
    ),
    classe_mb_slug: Optional[str] = Query(
        None,
        max_length=40,
        description="Com `nivel_mb` e `catalogo_por_classe_mb=true`, restringe tipo e círculo máximo (MB).",
    ),
    nivel_mb: Optional[int] = Query(
        None,
        ge=1,
        le=40,
        description="Nível de conjuração MB (ex.: tormenta_nivel_conjurador_mb ou nível do personagem).",
    ),
    catalogo_por_classe_mb: bool = Query(
        False,
        description="Se true, exige classe_mb_slug + nivel_mb e aplica lista arcana/divina + círculos lançáveis.",
    ),
    conjuracao_manual_mb: bool = Query(
        False,
        description="Se true, ignora restrição por classe (multiclasse / mesa).",
    ),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    response: Response = None,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaMagiaMbCatalogoPaginaResponse:
    tipo_filtro: str | None = None
    if tipo is not None and str(tipo).strip():
        tn = str(tipo).strip().lower()
        if tn in ("arcana", "divina"):
            tipo_filtro = tn
    circulo_max: int | None = None
    if catalogo_por_classe_mb and not conjuracao_manual_mb:
        slug = str(classe_mb_slug or "").strip().lower()
        if slug and nivel_mb is not None:
            t_auto = tipo_lista_magias_por_classe_mb(slug)
            if tipo_filtro is None and t_auto is not None:
                tipo_filtro = t_auto
            circulo_max = circulo_maximo_magias_lancaveis_mb(slug, int(nivel_mb))
    slice_rows, total = filtrar_magias_mb(
        q, circulo, tipo_filtro, escola, circulo_max, skip, limit
    )
    if response is not None:
        response.headers["X-Total-Count"] = str(total)
        response.headers["X-Skip"] = str(skip)
        response.headers["X-Limit"] = str(limit)
    itens = [TormentaMagiaMbCatalogoItem.model_validate(r) for r in slice_rows]
    return TormentaMagiaMbCatalogoPaginaResponse(itens=itens, total=total)


@router.get(
    "/conjuracao-mb",
    response_model=TormentaRegrasConjuracaoMbResponse,
    summary="Conjuração MB: habilidade-chave e PM por classe; custo em PM por círculo",
)
def obter_regras_conjuracao_mb(
    regra_versao: Optional[str] = Query(
        None,
        description="Edição: mb ou v13 (custo PM 1/3/6/10/15). Padrão mb.",
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasConjuracaoMbResponse:
    rv = normalizar_regra_versao(regra_versao)
    rows = lista_regras_conjuracao_por_versao(rv)
    classes = [TormentaConjuracaoClasseMbItem.model_validate(r) for r in rows]
    custo_pm_circulos = [
        TormentaConjuracaoCustoCirculoItem(
            circulo=c, custo_pm=custo_pm_preparar_ou_lancar_magia(c, rv)
        )
        for c in range(0, 10)
    ]
    return TormentaRegrasConjuracaoMbResponse(
        regra_versao=rv,
        classes=classes,
        custo_pm_circulos=custo_pm_circulos,
        nota_custo_magia=texto_custo_pm_por_circulo_mb(rv),
    )


@router.get(
    "/conjuracao-preview",
    response_model=TormentaConjuracaoPreviewResponse,
    summary="Pré-visualização MB: CD base (10+mod), modificador da chave e PM máx. de conjuração",
)
def obter_conjuracao_preview_mb(
    classe_slug: str = Query(
        ..., min_length=1, max_length=40, description="Slug MB da classe (ex.: mago)."
    ),
    nivel: int = Query(
        1,
        ge=1,
        le=40,
        description="Nível do personagem na ficha (fallback se nivel_conjurador omitido).",
    ),
    nivel_conjurador: Optional[int] = Query(
        None,
        ge=1,
        le=40,
        description="Override do nível de conjuração MB (multiclasse; espelha tormenta_nivel_conjurador_mb).",
    ),
    for_valor: int = Query(10, ge=0, le=99),
    des_valor: int = Query(10, ge=0, le=99),
    con_valor: int = Query(10, ge=0, le=99),
    int_valor: int = Query(10, ge=0, le=99),
    sab_valor: int = Query(10, ge=0, le=99),
    car_valor: int = Query(10, ge=0, le=99),
    regra_versao: Optional[str] = Query(
        None,
        description="Edição: mb ou v13. Padrão mb.",
    ),
    arcanista_caminho: Optional[str] = Query(
        None,
        max_length=16,
        description="Caminho arcanista v1.3: bruxo | mago | feiticeiro.",
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaConjuracaoPreviewResponse:
    rv = normalizar_regra_versao(regra_versao)
    slug = classe_slug.strip().lower()
    nv = int(nivel_conjurador) if nivel_conjurador is not None else int(nivel)
    if nv < 1:
        nv = 1
    if nv > 40:
        nv = 40
    hk = habilidade_chave_conjuracao(slug, rv, arcanista_caminho)
    mod = modificador_conjuracao_mb(
        slug,
        for_valor,
        des_valor,
        con_valor,
        int_valor,
        sab_valor,
        car_valor,
        regra_versao=rv,
        arcanista_caminho=arcanista_caminho,
    )
    if rv == REGRA_VERSAO_V13 and mod is not None:
        cd_magia = cd_resistencia_magia_t20(nv, mod, rv)
    else:
        cd_magia = (10 + mod) if mod is not None else None
    pm = pontos_magia_maximos_conjuracao(
        slug,
        nv,
        for_valor,
        des_valor,
        con_valor,
        int_valor,
        sab_valor,
        car_valor,
        regra_versao=rv,
        arcanista_caminho=arcanista_caminho,
    )
    lista_t = tipo_lista_magias_por_classe_mb(slug)
    cmax = circulo_maximo_magias_lancaveis_mb(slug, nv)
    return TormentaConjuracaoPreviewResponse(
        classe_slug=slug,
        nivel_conjuracao=nv,
        habilidade_chave=hk,
        modificador_conjuracao=mod,
        cd_magia=cd_magia,
        pontos_magia_maximos=pm,
        pontos_mana_maximos=pm,
        magias_lista_tipo=lista_t,
        magias_circulo_max=cmax,
    )


@router.get(
    "/escolhas-raciais",
    response_model=TormentaEscolhasRaciaisResponse,
    summary="Escolhas raciais v1.3 (Lefou, Qareen, Dahllan)",
)
def obter_escolhas_raciais(
    slug: str = Query(..., min_length=1, max_length=40),
    regra_versao: Optional[str] = Query(
        None,
        description="Edição: v13. Padrão v13.",
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaEscolhasRaciaisResponse:
    rv = normalizar_regra_versao(regra_versao or REGRA_VERSAO_V13)
    if rv != REGRA_VERSAO_V13:
        raise HTTPException(status_code=404, detail="Escolhas raciais só v1.3.")
    s = slug.strip().lower()
    cfg = escolhas_por_raca(s, rv)
    if not cfg:
        raise HTTPException(status_code=404, detail="Raça sem escolhas v1.3.")
    modos = None
    if cfg.get("modos"):
        modos = [TormentaEscolhaRacialModoItem(**m) for m in cfg["modos"]]
    asc = None
    if cfg.get("ascendencias"):
        asc = [TormentaEscolhaRacialAscendenciaItem(**a) for a in cfg["ascendencias"]]
    mag = None
    if cfg.get("magias_inatas"):
        mag = [TormentaEscolhaRacialMagiaInataItem(**m) for m in cfg["magias_inatas"]]
    mag_ops = None
    if cfg.get("magias_opcoes"):
        mag_ops = [
            TormentaEscolhaRacialMagiaOpcaoItem(**m) for m in cfg["magias_opcoes"]
        ]
    fontes = None
    if cfg.get("fontes"):
        fontes = [TormentaEscolhaRacialFonteItem(**f) for f in cfg["fontes"]]
    raca = TormentaEscolhasRaciaisRacaResponse(
        slug=s,
        tipo=str(cfg.get("tipo") or ""),
        bonus_pericia=cfg.get("bonus_pericia"),
        categoria_poder=cfg.get("categoria_poder"),
        modos=modos,
        ascendencias=asc,
        magias_inatas=mag,
        magia_circulo=cfg.get("magia_circulo"),
        magia_lista=cfg.get("magia_lista"),
        magia_atributo_chave=cfg.get("magia_atributo_chave"),
        escolhas_qtd=cfg.get("escolhas_qtd"),
        magias_opcoes=mag_ops,
        fontes=fontes,
        bonus_oficio=cfg.get("bonus_oficio"),
        slots_pericia=cfg.get("slots_pericia"),
    )
    return TormentaEscolhasRaciaisResponse(regra_versao=rv, raca=raca)


@router.get(
    "/tracos-raciais-preview",
    response_model=TormentaTracosRaciaisPreviewResponse,
    summary="Bônus mecânicos raciais (CA, resistências, perícias)",
)
def obter_tracos_raciais_preview(
    slug: str = Query(..., min_length=1, max_length=40),
    regra_versao: Optional[str] = Query(
        None,
        description="Edição: mb ou v13. Padrão mb.",
    ),
    humano_versatil: Optional[str] = Query(
        None,
        max_length=32,
        description="Humano v1.3: duas_pericias | pericia_poder",
    ),
    lefou_deformidade_modo: Optional[str] = Query(
        None,
        max_length=40,
        description="Lefou v1.3: duas_pericias | pericia_poder_tormenta",
    ),
    lefou_deformidade_pericias: Optional[str] = Query(
        None,
        max_length=500,
        description="Lefou v1.3: perícias separadas por vírgula.",
    ),
    qareen_ascendencia: Optional[str] = Query(
        None,
        max_length=40,
        description="Qareen v1.3: agua | ar | fogo | terra | luz | trevas",
    ),
    osteon_memoria_modo: Optional[str] = Query(
        None,
        max_length=40,
        description="Osteon v1.3: pericia | poder_geral",
    ),
    osteon_memoria_pericia: Optional[str] = Query(
        None,
        max_length=120,
    ),
    sereia_magias: Optional[str] = Query(
        None,
        max_length=200,
        description="Sereia v1.3: slugs de magias separados por vírgula.",
    ),
    golem_fonte_elemental: Optional[str] = Query(
        None,
        max_length=40,
        description="Golem v1.3: agua | ar | fogo | terra.",
    ),
    kliren_pericia: Optional[str] = Query(None, max_length=120),
    kliren_oficio: Optional[str] = Query(None, max_length=120),
    silfide_magias: Optional[str] = Query(
        None,
        max_length=200,
        description="Sílfide v1.3: slugs de magias separados por vírgula.",
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaTracosRaciaisPreviewResponse:
    per_lefou = None
    if lefou_deformidade_pericias:
        per_lefou = [
            p.strip() for p in str(lefou_deformidade_pericias).split(",") if p.strip()
        ]
    mag_sereia = None
    if sereia_magias:
        mag_sereia = [
            p.strip().lower() for p in str(sereia_magias).split(",") if p.strip()
        ]
    mag_silfide = None
    if silfide_magias:
        mag_silfide = [
            p.strip().lower() for p in str(silfide_magias).split(",") if p.strip()
        ]
    data = preview_tracos_raciais(
        slug.strip().lower(),
        regra_versao=regra_versao,
        humano_versatil=humano_versatil,
        lefou_deformidade_modo=lefou_deformidade_modo,
        lefou_deformidade_pericias=per_lefou,
        qareen_ascendencia=qareen_ascendencia,
        osteon_memoria_modo=osteon_memoria_modo,
        osteon_memoria_pericia=osteon_memoria_pericia,
        sereia_magias=mag_sereia,
        golem_fonte_elemental=golem_fonte_elemental,
        kliren_pericia=kliren_pericia,
        kliren_oficio=kliren_oficio,
        silfide_magias=mag_silfide,
    )
    return TormentaTracosRaciaisPreviewResponse(**data)


@router.get(
    "/pericias",
    response_model=TormentaRegrasPericiasResponse,
    summary="Tabela de DCs padrão e bônus de treinamento",
)
def obter_regras_pericias(
    regra_versao: Optional[str] = Query(
        None,
        description="Versão de regras: mb ou v13. Default: mb.",
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasPericiasResponse:
    from app.games.tormenta.schemas.regras_ficha import TormentaDificuldadePadraoItem

    rv = normalizar_regra_versao(regra_versao)
    dcs = [
        TormentaDificuldadePadraoItem(**row) for row in lista_dificuldades_padrao_mb()
    ]
    niveis_v13 = None
    bonus = 2
    if rv == "v13":
        bonus = 2
        niveis_v13 = [
            {"nivel_min": 1, "nivel_max": 6, "bonus": 2},
            {"nivel_min": 7, "nivel_max": 14, "bonus": 4},
            {"nivel_min": 15, "nivel_max": 40, "bonus": 6},
        ]
    return TormentaRegrasPericiasResponse(
        regra_versao=rv,
        dificuldades=dcs,
        bonus_treinado=bonus,
        bonus_treinamento_niveis=niveis_v13,
    )


@router.post(
    "/pericias/calcular-bonus",
    response_model=TormentaPericiaBonusResponse,
    summary="Calcula bônus total de perícia",
)
def calcular_bonus_pericia_mb(
    body: TormentaPericiaBonusRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaPericiaBonusResponse:
    rv = normalizar_regra_versao(body.regra_versao)
    racial = int(body.racial_bonus)
    if body.slug_raca and body.nome_pericia:
        racial = racial_bonus_pericia(body.slug_raca, body.nome_pericia, rv)
    pode, motivo = pode_usar_pericia_treinada(
        body.nome_pericia or "", body.treinado, rv
    )
    if body.itens_protecao is not None:
        meta = meta_pericia_por_nome(body.nome_pericia or "", rv)
        pen_arm = penalidade_armadura_pericia(
            meta,
            body.itens_protecao,
            uso_atletismo_natacao=body.uso_atletismo_natacao,
            slug_classe=body.tormenta_classe_mb_slug,
        )
    else:
        pen_arm = int(body.penalidade_armadura)
    meta_pen = meta_pericia_por_nome(body.nome_pericia or "", rv)
    nao_prof = False
    if body.itens_protecao is not None:
        nao_prof = tem_protecao_sem_proficiencia(
            body.itens_protecao, body.tormenta_classe_mb_slug
        )
    if body.penalidade_sobrecarga_carga and pericia_aplica_penalidade_armadura(
        meta_pen,
        uso_atletismo_natacao=body.uso_atletismo_natacao,
        nao_proficiente_armadura=nao_prof,
    ):
        pen_arm += PENALIDADE_SOBRECARGA
    bonus = calcular_bonus_pericia(
        nivel=body.nivel,
        mod_atributo=body.mod_atributo,
        treinado=body.treinado,
        graduacao=body.graduacao,
        outros=body.outros,
        racial_bonus=racial,
        penalidade_armadura=pen_arm,
        pericia_de_classe=body.pericia_de_classe,
        regra_versao=rv,
    )
    meio = body.nivel // 2
    tre = bonus_treinamento_por_nivel(body.nivel, rv) if body.treinado else 0
    pp = None
    nome_norm = (body.nome_pericia or "").strip().lower()
    if nome_norm in ("percepção", "percepcao"):
        pp = percepcao_passiva_t20(bonus)
    return TormentaPericiaBonusResponse(
        bonus_total=bonus,
        meio_nivel=meio,
        bonus_treinamento=tre,
        penalidade_armadura_aplicada=pen_arm,
        percepcao_passiva=pp,
        pode_usar=pode,
        motivo_bloqueio=motivo,
    )


@router.post(
    "/pericias/rolar",
    response_model=TormentaPericiaRolarResponse,
    summary="Rola teste de perícia 1d20 + bônus vs DC",
)
def rolar_pericia_mb(
    body: TormentaPericiaRolarRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaPericiaRolarResponse:
    data = rolar_teste_pericia(body.bonus, body.dc)
    return TormentaPericiaRolarResponse(**data)


@router.post(
    "/ataque/ajustar-bonus",
    response_model=TormentaAtaqueBonusResponse,
    summary="Ajusta bônus de ataque v1.3 (−5 se não proficiente na arma)",
)
def ajustar_bonus_ataque_v13_api(
    body: TormentaAtaqueBonusRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaAtaqueBonusResponse:
    data = ajustar_bonus_ataque_v13(
        body.bonus_base,
        body.tormenta_classe_mb_slug,
        nome_arma=body.nome_arma,
        proficiencia_arma=body.proficiencia_arma,
    )
    return TormentaAtaqueBonusResponse(**data)


@router.post(
    "/carga-preview",
    response_model=TormentaCargaPreviewResponse,
    summary="Calcula carga v1.3 (espaços, limite, sobrecarga)",
)
def preview_carga_tormenta_v13(
    body: TormentaCargaPreviewRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaCargaPreviewResponse:
    raw = preview_carga_v13(
        for_valor=body.for_valor,
        itens=[i.model_dump() for i in body.itens],
        moedas_total=body.moedas_total,
    )
    return TormentaCargaPreviewResponse(
        limite=raw["limite"],
        limite_maximo=raw["limite_maximo"],
        espacos_usados=raw["espacos_usados"],
        espacos_itens=raw["espacos_itens"],
        espacos_moedas=raw["espacos_moedas"],
        estado=raw["estado"],
        sobrecarga=raw["sobrecarga"],
        penalidade_armadura_extra=raw["penalidade_armadura_extra"],
        deslocamento_extra_m=raw["deslocamento_extra_m"],
        detalhes=[TormentaCargaDetalheItem(**d) for d in raw.get("detalhes") or []],
    )


@router.get(
    "/pv-preview",
    response_model=TormentaPvPreviewResponse,
    summary="PV máximos por classe, nível e CON",
)
def obter_pv_preview_mb(
    classe_slug: str = Query(..., min_length=1, max_length=40),
    nivel: int = Query(1, ge=1, le=40),
    con_valor: int = Query(10, ge=-99, le=99),
    for_valor: int = Query(10, ge=-99, le=99),
    des_valor: int = Query(10, ge=-99, le=99),
    int_valor: int = Query(10, ge=-99, le=99),
    sab_valor: int = Query(10, ge=-99, le=99),
    car_valor: int = Query(10, ge=-99, le=99),
    regra_versao: Optional[str] = Query(
        None,
        description="Versão de regras: mb ou v13. Default: mb.",
    ),
    arcanista_caminho: Optional[str] = Query(
        None,
        max_length=16,
        description="Caminho do arcanista v1.3: bruxo | mago | feiticeiro.",
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaPvPreviewResponse:
    rv = normalizar_regra_versao(regra_versao)
    data = preview_pv_mb(
        classe_slug.strip().lower(),
        nivel,
        con_valor,
        regra_versao=rv,
        arcanista_caminho=arcanista_caminho,
        for_valor=for_valor,
        des_valor=des_valor,
        int_valor=int_valor,
        sab_valor=sab_valor,
        car_valor=car_valor,
    )
    return TormentaPvPreviewResponse(**data)


@router.post(
    "/pm-preview-multiclasse",
    response_model=TormentaPmMulticlassePreviewResponse,
    summary="PM máximos v1.3 — soma multiclasse (nível × pm/nível por classe)",
)
def obter_pm_preview_multiclasse_v13(
    body: TormentaPmMulticlassePreviewRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaPmMulticlassePreviewResponse:
    rv = normalizar_regra_versao(body.regra_versao or REGRA_VERSAO_V13)
    if rv != REGRA_VERSAO_V13:
        raise HTTPException(
            status_code=400,
            detail="PM multiclasse por soma só está disponível na regra v1.3.",
        )
    classes = [{"slug": c.slug.strip().lower(), "nivel": c.nivel} for c in body.classes]
    data = preview_pm_multiclasse_v13(classes)
    return TormentaPmMulticlassePreviewResponse(**data)


@router.get(
    "/dinheiro-inicial",
    response_model=TormentaDinheiroInicialResponse,
    summary="Dinheiro inicial v1.3 — Tabela 3-1 por nível",
)
def obter_dinheiro_inicial_v13(
    nivel: int = Query(1, ge=1, le=40),
    regra_versao: Optional[str] = Query(
        None,
        description="Versão de regras: v13 (padrão).",
    ),
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaDinheiroInicialResponse:
    rv = normalizar_regra_versao(regra_versao or REGRA_VERSAO_V13)
    if rv != REGRA_VERSAO_V13:
        raise HTTPException(
            status_code=400,
            detail="Tabela 3-1 de dinheiro inicial só está disponível na regra v1.3.",
        )
    data = preview_dinheiro_inicial_v13(nivel)
    return TormentaDinheiroInicialResponse(**data)


@router.get(
    "/pericias-classe-preview",
    summary="Perícias de classe v1.3: fixas, grupos «ou» e pool de escolha",
)
def obter_pericias_classe_preview(
    classe_slug: str = Query(..., min_length=1, max_length=40),
    _: Usuario = Depends(get_usuario_atual),
) -> dict:
    data = preview_pericias_classe_v13(classe_slug.strip().lower())
    if not data:
        raise HTTPException(status_code=404, detail="Classe v1.3 não encontrada.")
    return data


@router.post(
    "/pericias/validar-criacao",
    response_model=TormentaPericiasValidarCriacaoResponse,
    summary="Valida orçamento de perícias treinadas (e graduações MB)",
)
def validar_pericias_criacao_mb(
    body: TormentaPericiasValidarCriacaoRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaPericiasValidarCriacaoResponse:
    rv = normalizar_regra_versao(body.regra_versao)
    pericias = [p.model_dump() for p in body.pericias]
    data = preview_pericias_criacao(
        nivel=body.nivel,
        slug_classe=body.classe_slug.strip().lower(),
        int_valor=body.int_valor,
        slug_raca=(body.slug_raca or "").strip().lower() or None,
        pericias=pericias,
        regra_versao=rv,
        humano_versatil=body.humano_versatil,
        origem_beneficios=body.origem_beneficios,
    )
    return TormentaPericiasValidarCriacaoResponse(**data)


@router.post(
    "/poderes/validar-pre-requisitos",
    response_model=TormentaPoderValidarPreRequisitosResponse,
    summary="Valida pré-requisitos de poder v1.3 (RF-T08g)",
)
def validar_pre_requisitos_poder_v13(
    body: TormentaPoderValidarPreRequisitosRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaPoderValidarPreRequisitosResponse:
    rv = normalizar_regra_versao(body.regra_versao or REGRA_VERSAO_V13)
    if rv != REGRA_VERSAO_V13:
        return TormentaPoderValidarPreRequisitosResponse(
            valido=True,
            nome_poder=body.nome_poder.strip(),
            faltando=[],
            pre_requisitos=[],
            motivo="",
        )
    data = TormentaPersonagemTalentosService.preview_validar_pre_requisitos(
        body.model_dump()
    )
    return TormentaPoderValidarPreRequisitosResponse(**data)
