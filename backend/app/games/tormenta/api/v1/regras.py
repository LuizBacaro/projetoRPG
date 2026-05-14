"""HTTP — regras de ficha Tormenta 20 (dados estáticos para o frontend)."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response

from app.games.tormenta.schemas.regras_ficha import (
    TormentaArmaduraCatalogoItem,
    TormentaArmaduraCatalogoPaginaResponse,
    TormentaBeneficioNivelMbItem,
    TormentaClasseMbItem,
    TormentaConjuracaoCustoCirculoItem,
    TormentaConjuracaoClasseMbItem,
    TormentaCustoAtributoItem,
    TormentaDivindadeMbOpcao,
    TormentaIdiomaTabelaItem,
    TormentaPericiaAtributoItem,
    TormentaRacaMbItem,
    TormentaCatalogoItem,
    TormentaCatalogoPaginaResponse,
    TormentaMagiaMbCatalogoItem,
    TormentaMagiaMbCatalogoPaginaResponse,
    TormentaRegrasConjuracaoMbResponse,
    TormentaConjuracaoPreviewResponse,
    TormentaRegrasAtributosResponse,
    TormentaRegrasClassesResponse,
    TormentaRegrasIdentidadeMbResponse,
    TormentaRegrasRacasResponse,
)
from app.games.tormenta.rules.atributos_t20 import (
    lista_custos_compra,
    lista_pericias_com_atributo,
    pontos_iniciais_compra,
)
from app.games.tormenta.rules.classes_t20 import lista_beneficios_por_nivel_mb, lista_classes_mb
from app.games.tormenta.rules.catalogo_armaduras_t20 import filtrar_armaduras_protecao_mb
from app.games.tormenta.rules.catalogo_t20 import filtrar_equipamentos_mb, filtrar_magias_mb, filtrar_talentos_mb
from app.games.tormenta.rules.magias_progressao_mb_t20 import (
    circulo_maximo_magias_lancaveis_mb,
    tipo_lista_magias_por_classe_mb,
)
from app.games.tormenta.rules.racas_t20 import idiomas_mb_extras, lista_racas_mb
from app.games.tormenta.rules.tendencias_divindades_t20 import lista_divindades_mb, lista_tendencias_mb
from app.games.tormenta.rules.conjuracao_t20 import (
    custo_pm_preparar_ou_lancar_magia,
    habilidade_chave_conjuracao,
    lista_regras_conjuracao_classe_mb,
    modificador_conjuracao_mb,
    pontos_magia_maximos_conjuracao,
    texto_custo_pm_por_circulo_mb,
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
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasAtributosResponse:
    custos = [TormentaCustoAtributoItem(**row) for row in lista_custos_compra()]
    pericias = [TormentaPericiaAtributoItem(**row) for row in lista_pericias_com_atributo()]
    return TormentaRegrasAtributosResponse(
        pontos_compra_iniciais=pontos_iniciais_compra(),
        custos=custos,
        pericias=pericias,
    )


@router.get(
    "/racas",
    response_model=TormentaRegrasRacasResponse,
    summary="Raças do Módulo Básico (ajustes, traços, idioma racial) + regra e tabela de idiomas MB",
)
def obter_regras_racas(
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasRacasResponse:
    geral, tabela = idiomas_mb_extras()
    racas = [TormentaRacaMbItem(**row) for row in lista_racas_mb()]
    idiomas_rows = [TormentaIdiomaTabelaItem(**row) for row in tabela]
    return TormentaRegrasRacasResponse(
        racas=racas,
        idiomas_geral_mb=geral,
        idiomas_tabela_mb=idiomas_rows,
    )


@router.get(
    "/classes",
    response_model=TormentaRegrasClassesResponse,
    summary="Benefícios por nível (MB) e classes com BBA, PV e perícias",
)
def obter_regras_classes(
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasClassesResponse:
    ben = [TormentaBeneficioNivelMbItem(**row) for row in lista_beneficios_por_nivel_mb()]
    cls_rows = [TormentaClasseMbItem(**row) for row in lista_classes_mb()]
    return TormentaRegrasClassesResponse(beneficios_por_nivel=ben, classes=cls_rows)


@router.get(
    "/identidade-mb",
    response_model=TormentaRegrasIdentidadeMbResponse,
    summary="Tendências (alinhamento) e divindades MB para combos na ficha",
)
def obter_regras_identidade_mb(
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasIdentidadeMbResponse:
    div_rows = [TormentaDivindadeMbOpcao(**row) for row in lista_divindades_mb()]
    return TormentaRegrasIdentidadeMbResponse(
        tendencias=lista_tendencias_mb(),
        divindades=div_rows,
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
def listar_catalogo_talentos(
    q: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=200),
    response: Response = None,
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaCatalogoPaginaResponse:
    slice_rows, total = filtrar_talentos_mb(q, skip, limit)
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
    "/magias",
    response_model=TormentaMagiaMbCatalogoPaginaResponse,
    summary="Catálogo MB de magias (metadados; busca e paginação)",
)
def listar_catalogo_magias(
    q: Optional[str] = None,
    circulo: Optional[int] = Query(None, ge=0, le=20, description="0 = truque; omitir para todos."),
    tipo: Optional[str] = Query(None, description="arcana ou divina."),
    escola: Optional[str] = Query(None, description="Substring na escola (ex.: Abjuração)."),
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
    slice_rows, total = filtrar_magias_mb(q, circulo, tipo_filtro, escola, circulo_max, skip, limit)
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
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaRegrasConjuracaoMbResponse:
    rows = lista_regras_conjuracao_classe_mb()
    classes = [TormentaConjuracaoClasseMbItem.model_validate(r) for r in rows]
    custo_pm_circulos = [
        TormentaConjuracaoCustoCirculoItem(circulo=c, custo_pm=custo_pm_preparar_ou_lancar_magia(c))
        for c in range(0, 10)
    ]
    return TormentaRegrasConjuracaoMbResponse(
        classes=classes,
        custo_pm_circulos=custo_pm_circulos,
        nota_custo_magia=texto_custo_pm_por_circulo_mb(),
    )


@router.get(
    "/conjuracao-preview",
    response_model=TormentaConjuracaoPreviewResponse,
    summary="Pré-visualização MB: CD base (10+mod), modificador da chave e PM máx. de conjuração",
)
def obter_conjuracao_preview_mb(
    classe_slug: str = Query(..., min_length=1, max_length=40, description="Slug MB da classe (ex.: mago)."),
    nivel: int = Query(1, ge=1, le=40, description="Nível do personagem na ficha (fallback se nivel_conjurador omitido)."),
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
    _: Usuario = Depends(get_usuario_atual),
) -> TormentaConjuracaoPreviewResponse:
    slug = classe_slug.strip().lower()
    nv = int(nivel_conjurador) if nivel_conjurador is not None else int(nivel)
    if nv < 1:
        nv = 1
    if nv > 40:
        nv = 40
    hk = habilidade_chave_conjuracao(slug)
    mod = modificador_conjuracao_mb(
        slug,
        for_valor,
        des_valor,
        con_valor,
        int_valor,
        sab_valor,
        car_valor,
    )
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
