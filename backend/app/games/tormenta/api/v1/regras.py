"""HTTP — regras de ficha Tormenta 20 (dados estáticos para o frontend)."""

from fastapi import APIRouter, Depends

from app.games.tormenta.schemas.regras_ficha import (
    TormentaBeneficioNivelMbItem,
    TormentaClasseMbItem,
    TormentaCustoAtributoItem,
    TormentaIdiomaTabelaItem,
    TormentaPericiaAtributoItem,
    TormentaRacaMbItem,
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
