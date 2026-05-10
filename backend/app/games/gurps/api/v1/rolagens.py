"""HTTP — utilitários de rolagem GURPS."""

from fastapi import APIRouter, Depends, HTTPException

from app.games.gurps.core.rolagem import (
    avaliar_teste_3d6,
    calcular_nivel_efetivo,
    rolar_dano,
)
from app.games.gurps.schemas.rolagem import (
    GurpsDanoRequest,
    GurpsDanoResponse,
    GurpsNivelEfetivoRequest,
    GurpsNivelEfetivoResponse,
    GurpsTeste3d6Request,
    GurpsTeste3d6Response,
)
from app.shared.core.deps import requer_game_gurps

router = APIRouter(
    prefix="/gurps/rolagens",
    tags=["GURPS — Rolagens"],
    dependencies=[Depends(requer_game_gurps)],
)


@router.post("/3d6", response_model=GurpsTeste3d6Response)
def rolar_teste_3d6(payload: GurpsTeste3d6Request):
    try:
        out = avaliar_teste_3d6(payload.nivel_efetivo, dados=payload.dados)
        return GurpsTeste3d6Response(
            dados=out.dados,
            total=out.total,
            nivel_efetivo=out.nivel_efetivo,
            sucesso=out.sucesso,
            margem=out.margem,
            sucesso_decisivo=out.sucesso_decisivo,
            falha_critica=out.falha_critica,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/nivel-efetivo", response_model=GurpsNivelEfetivoResponse)
def calcular_alvo_teste(payload: GurpsNivelEfetivoRequest):
    soma_modificadores = int(sum(payload.modificadores or []))
    nivel_efetivo = calcular_nivel_efetivo(payload.nh_base, payload.modificadores)
    return GurpsNivelEfetivoResponse(
        nh_base=payload.nh_base,
        modificadores=payload.modificadores,
        soma_modificadores=soma_modificadores,
        nivel_efetivo=nivel_efetivo,
    )


@router.post("/dano", response_model=GurpsDanoResponse)
def rolar_dano_por_expressao(payload: GurpsDanoRequest):
    try:
        out = rolar_dano(payload.expressao)
        return GurpsDanoResponse(
            expressao=out.expressao,
            dados_rolados=out.dados_rolados,
            quantidade_dados=out.quantidade_dados,
            modificador=out.modificador,
            total_sem_modificador=out.total_sem_modificador,
            total=out.total,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
