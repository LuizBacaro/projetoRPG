"""HTTP — regras de ficha Tormenta 20 (dados estáticos para o frontend)."""

from typing import Optional

from fastapi import APIRouter, Depends, Query, Response

from app.games.tormenta.schemas.regras_ficha import (
    TormentaArmaduraCatalogoItem,
    TormentaArmaduraCatalogoPaginaResponse,
    TormentaBeneficioNivelMbItem,
    TormentaClasseMbItem,
    TormentaCustoAtributoItem,
    TormentaIdiomaTabelaItem,
    TormentaPericiaAtributoItem,
    TormentaRacaMbItem,
    TormentaCatalogoItem,
    TormentaCatalogoPaginaResponse,
    TormentaRegrasAtributosResponse,
    TormentaRegrasClassesResponse,
    TormentaRegrasRacasResponse,
)
from app.games.tormenta.rules.atributos_t20 import (
    lista_custos_compra,
    lista_pericias_com_atributo,
    pontos_iniciais_compra,
)
from app.games.tormenta.rules.classes_t20 import lista_beneficios_por_nivel_mb, lista_classes_mb
from app.games.tormenta.rules.catalogo_armaduras_t20 import filtrar_armaduras_protecao_mb
from app.games.tormenta.rules.catalogo_t20 import filtrar_equipamentos_mb, filtrar_talentos_mb
from app.games.tormenta.rules.racas_t20 import idiomas_mb_extras, lista_racas_mb
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
