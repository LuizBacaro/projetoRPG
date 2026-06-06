"""HTTP — arena de combate D&D 5e (iniciativa, ataque, dano)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_dnd5e_conjuracao_service
from app.games.dnd5e.rules.combate import (
    ArmaCombate,
    aplicar_dano_hp,
    aplicar_teste_morte,
    calcular_dano,
    calcular_iniciativa,
    economia_turno_de_dict,
    estabilizar_combatente,
    gastar_acao_turno,
    ordenar_chave_iniciativa,
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
    Dnd5eConcentracaoTesteRequest,
    Dnd5eConcentracaoTesteResponse,
    Dnd5eDeathSaveRequest,
    Dnd5eDeathSaveResponse,
    Dnd5eDanoHpRequest,
    Dnd5eDanoHpResponse,
    Dnd5eEstabilizarRequest,
    Dnd5eEstabilizarResponse,
    Dnd5eEconomiaTurnoRequest,
    Dnd5eEconomiaTurnoResponse,
    Dnd5eEconomiaTurnoState,
    Dnd5eCondicaoAtivaItem,
    Dnd5eCondicoesTurnoRequest,
    Dnd5eCondicoesTurnoResponse,
    Dnd5eConjurarRequest,
    Dnd5eConjurarResponse,
    Dnd5eDanoRequest,
    Dnd5eDanoResponse,
    Dnd5eIniciativaRequest,
    Dnd5eIniciativaResponse,
    Dnd5eIniciativaResultado,
    Dnd5eSincronizarHpCondicoesRequest,
)
from app.games.dnd5e.services.conjuracao_service import Dnd5eConjuracaoService
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
    resultados.sort(
        key=lambda r: ordenar_chave_iniciativa(r.iniciativa, r.dex_mod, r.nome)
    )
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
        is_critico=resultado.is_critico,
    )


@router.post(
    "/death-save",
    response_model=Dnd5eDeathSaveResponse,
    summary="Salvamento contra morte (1d20 no início do turno com 0 PV)",
)
def rolar_death_save(
    payload: Dnd5eDeathSaveRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eDeathSaveResponse:
    roll = payload.rolagem_d20 if payload.rolagem_d20 is not None else rolar_d20()
    resultado = aplicar_teste_morte(
        payload.hp_atual,
        payload.death_failures,
        payload.death_successes,
        roll,
    )
    mensagens = {
        "vivo": (
            "20 natural! Recuperou 1 PV e voltou à consciência."
            if roll == 20
            else "Personagem recuperou consciência (PV > 0)."
        ),
        "inconsciente": "Ainda inconsciente — continue salvamentos.",
        "estabilizado": "Estabilizado (3 sucessos).",
        "morto": "Morto (3 falhas).",
    }
    return Dnd5eDeathSaveResponse(
        rolagem=roll,
        death_failures=resultado.death_failures,
        death_successes=resultado.death_successes,
        hp_atual=resultado.hp_atual,
        status_vida=resultado.status.value,
        mensagem=mensagens.get(resultado.status.value, resultado.status.value),
    )


@router.post(
    "/dano-hp",
    response_model=Dnd5eDanoHpResponse,
    summary="Aplica dano com regras de morte (0 PV, morte instantânea, estabilizado)",
)
def aplicar_dano_com_regras_morte(
    payload: Dnd5eDanoHpRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eDanoHpResponse:
    resultado = aplicar_dano_hp(
        payload.hp_atual,
        payload.hp_max,
        payload.death_failures,
        payload.death_successes,
        payload.dano,
        is_critico=payload.is_critico,
        status_vida=payload.status_vida,
    )
    if resultado.morte_instantanea:
        msg = "Morte instantânea (dano excedente ≥ PV máximo)."
    elif resultado.status.value == "morto":
        msg = "Morto (3 falhas em salvamentos)."
    elif payload.hp_atual > 0 and resultado.hp_atual == 0:
        msg = "Caiu inconsciente (0 PV)."
    elif payload.hp_atual == 0 and payload.dano > 0:
        extra = "crítico — 2 falhas" if payload.is_critico else "1 falha"
        msg = f"Dano com 0 PV: +{extra} em salvamentos."
    else:
        msg = f"Dano aplicado — PV {resultado.hp_atual}."
    return Dnd5eDanoHpResponse(
        hp_atual=resultado.hp_atual,
        death_failures=resultado.death_failures,
        death_successes=resultado.death_successes,
        status_vida=resultado.status.value,
        morte_instantanea=resultado.morte_instantanea,
        mensagem=msg,
    )


@router.post(
    "/estabilizar",
    response_model=Dnd5eEstabilizarResponse,
    summary="Estabiliza combatente a 0 PV (Medicina CD 10 ou magia)",
)
def estabilizar_em_combate(
    payload: Dnd5eEstabilizarRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eEstabilizarResponse:
    try:
        resultado = estabilizar_combatente(
            payload.hp_atual,
            metodo=payload.metodo,
            mod_medicina=payload.mod_medicina,
            rolagem_d20=payload.rolagem_d20,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    if resultado.sucesso:
        msg = (
            "Estabilizado por magia/efeito."
            if payload.metodo.strip().lower() == "magia"
            else f"Medicina ({resultado.total_medicina}) — estabilizado."
        )
    else:
        msg = (
            f"Medicina falhou ({resultado.total_medicina} < 10) — "
            "ainda inconsciente."
        )
    return Dnd5eEstabilizarResponse(
        death_failures=resultado.death_failures,
        death_successes=resultado.death_successes,
        status_vida=resultado.status.value,
        sucesso=resultado.sucesso,
        rolagem=resultado.rolagem,
        total_medicina=resultado.total_medicina,
        mensagem=msg,
    )


@router.post(
    "/turno/economia",
    response_model=Dnd5eEconomiaTurnoResponse,
    summary="Gasta ou reinicia economia de ações do turno (PHB)",
)
def atualizar_economia_turno(
    payload: Dnd5eEconomiaTurnoRequest,
    _: Usuario = Depends(get_usuario_atual),
) -> Dnd5eEconomiaTurnoResponse:
    atual = economia_turno_de_dict(payload.economia.model_dump())
    try:
        nova = gastar_acao_turno(atual, payload.tipo, metros=payload.metros)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    estado = Dnd5eEconomiaTurnoState(**nova.as_dict())
    msg = "Economia reiniciada." if payload.tipo == "reset" else f"Ação '{payload.tipo}' registrada."
    return Dnd5eEconomiaTurnoResponse(economia=estado, mensagem=msg)


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


@router.post(
    "/conjurar",
    response_model=Dnd5eConjurarResponse,
    summary="Gasta espaço de magia, calcula CD e dano (se houver)",
)
def conjurar_magia_combate(
    payload: Dnd5eConjurarRequest,
    _: Usuario = Depends(get_usuario_atual),
    service: Dnd5eConjuracaoService = Depends(get_dnd5e_conjuracao_service),
) -> Dnd5eConjurarResponse:
    return service.conjurar(payload)


@router.post(
    "/concentracao-teste",
    response_model=Dnd5eConcentracaoTesteResponse,
    summary="Teste de concentração ao receber dano (PHB 5e)",
)
def teste_concentracao_combate(
    payload: Dnd5eConcentracaoTesteRequest,
    _: Usuario = Depends(get_usuario_atual),
    service: Dnd5eConjuracaoService = Depends(get_dnd5e_conjuracao_service),
) -> Dnd5eConcentracaoTesteResponse:
    return service.teste_concentracao(payload)
