"""HTTP — arena de combate D&D 5e (iniciativa, ataque, dano)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.games.dnd5e.rules.combate import (
    ArmaCombate,
    calcular_dano,
    calcular_iniciativa,
    resolver_ataque,
)
from app.games.dnd5e.rules.condicoes_ficha import (
    decrementar_condicoes_turno,
    normalizar_condicoes_ficha,
    sincronizar_condicoes_por_hp,
)
from app.games.dnd5e.rules.dados import rolar_d20
from app.games.dnd5e.schemas.combate import (
    Dnd5eAtaqueRequest,
    Dnd5eAtaqueResponse,
    Dnd5eCondicaoAtivaItem,
    Dnd5eCondicoesTurnoRequest,
    Dnd5eCondicoesTurnoResponse,
    Dnd5eDanoRequest,
    Dnd5eDanoResponse,
    Dnd5eIniciativaRequest,
    Dnd5eIniciativaResponse,
    Dnd5eIniciativaResultado,
    Dnd5eSincronizarHpCondicoesRequest,
)
from app.shared.core.deps import get_usuario_atual, requer_game_dnd5e
from app.shared.models.usuario import Usuario

router = APIRouter(
    prefix="/dnd5e/combate",
    tags=["D&D 5e — Combate"],
    dependencies=[Depends(requer_game_dnd5e)],
)


@router.post(
    "/iniciativa",
    response_model=Dnd5eIniciativaResponse,
    summary="Rola iniciativa (1d20 + DES) e devolve ordem decrescente",
)
def rolar_iniciativa_combate(
    payload: Dnd5eIniciativaRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eIniciativaResponse:
    resultados: list[Dnd5eIniciativaResultado] = []
    for c in payload.combatentes:
        roll = rolar_d20()
        total = calcular_iniciativa(c.dex_mod, rolagem_d20=roll)
        resultados.append(
            Dnd5eIniciativaResultado(
                id=c.id,
                nome=c.nome,
                dex_mod=c.dex_mod,
                rolagem=roll,
                iniciativa=total,
            )
        )
    resultados.sort(key=lambda r: (-r.iniciativa, -r.rolagem, r.nome))
    return Dnd5eIniciativaResponse(ordem=resultados)


@router.post(
    "/ataque",
    response_model=Dnd5eAtaqueResponse,
    summary="Testa se ataque atinge CA (PHB)",
)
def resolver_ataque_endpoint(
    payload: Dnd5eAtaqueRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eAtaqueResponse:
    resultado = resolver_ataque(
        payload.mod_atributo,
        payload.bonus_proficiencia,
        payload.ac_alvo,
        rolagem_d20=payload.rolagem_d20,
        proficiente=payload.proficiente,
        bonus_extra=payload.bonus_extra,
        condicoes_atacante=payload.condicoes_atacante,
        condicoes_alvo=payload.condicoes_alvo,
        corpo_a_corpo=payload.corpo_a_corpo,
    )
    return Dnd5eAtaqueResponse(
        rolagem=resultado.rolagem,
        rolagem_secundaria=resultado.rolagem_secundaria,
        total=resultado.total,
        acerto=resultado.acerto,
        vantagem=resultado.vantagem,
        desvantagem=resultado.desvantagem,
        critico_automatico=resultado.critico_automatico,
        acerto_automatico=resultado.acerto_automatico,
    )


@router.post(
    "/condicoes/decrementar-turno",
    response_model=Dnd5eCondicoesTurnoResponse,
    summary="Decrementa duração das condições ao fim do turno do combatente",
)
def decrementar_condicoes_combate_turno(
    payload: Dnd5eCondicoesTurnoRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eCondicoesTurnoResponse:
    atualizadas = decrementar_condicoes_turno(
        [c.model_dump() for c in payload.condicoes]
    )
    return Dnd5eCondicoesTurnoResponse(
        condicoes=[Dnd5eCondicaoAtivaItem(**row) for row in atualizadas]
    )


@router.post(
    "/condicoes/normalizar",
    response_model=Dnd5eCondicoesTurnoResponse,
    summary="Valida slugs e normaliza lista de condições ativas",
)
def normalizar_condicoes_combate(
    payload: Dnd5eCondicoesTurnoRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eCondicoesTurnoResponse:
    normalizadas = normalizar_condicoes_ficha(
        [c.model_dump() for c in payload.condicoes]
    )
    return Dnd5eCondicoesTurnoResponse(
        condicoes=[Dnd5eCondicaoAtivaItem(**row) for row in normalizadas]
    )


@router.post(
    "/condicoes/sincronizar-hp",
    response_model=Dnd5eCondicoesTurnoResponse,
    summary="Aplica/remove inconsciente automático conforme PV atual",
)
def sincronizar_condicoes_hp_combate(
    payload: Dnd5eSincronizarHpCondicoesRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eCondicoesTurnoResponse:
    atualizadas = sincronizar_condicoes_por_hp(
        payload.hp_atual,
        [c.model_dump(exclude_none=True) for c in payload.condicoes],
    )
    return Dnd5eCondicoesTurnoResponse(
        condicoes=[Dnd5eCondicaoAtivaItem(**row) for row in atualizadas]
    )


@router.post(
    "/dano",
    response_model=Dnd5eDanoResponse,
    summary="Rola dano de arma (NdM + mod; crítico dobra dados)",
)
def resolver_dano(
    payload: Dnd5eDanoRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eDanoResponse:
    try:
        if payload.rolagem_forcada is not None:
            total = max(1, payload.rolagem_forcada + payload.mod_atributo)
        else:
            total = calcular_dano(
                ArmaCombate(dano=payload.dano),
                payload.mod_atributo,
                is_critico=payload.is_critico,
            )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    return Dnd5eDanoResponse(dano_total=total)
