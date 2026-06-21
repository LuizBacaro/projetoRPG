"""Ataque de oportunidade PHB — reação ao sair do alcance corpo a corpo."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence

from app.games.dnd5e.rules.arma_combate import resolver_ataque_com_arma
from app.games.dnd5e.rules.combate import EconomiaTurno, gastar_acao_turno


def validar_oportunidade(
    economia_atacante: EconomiaTurno,
    *,
    alvo_desengajado: bool = False,
) -> None:
    if alvo_desengajado:
        raise ValueError("Alvo usou Desengajar — sem ataque de oportunidade")
    if economia_atacante.reacao_usada:
        raise ValueError("Reação já usada nesta rodada")


def resolver_ataque_oportunidade(
    *,
    str_mod: int,
    dex_mod: int,
    bonus_proficiencia: int,
    ac_alvo: int,
    arma_slug: Optional[str] = None,
    feats: Optional[List[str]] = None,
    raca_slug: str = "",
    rolagem_d20: Optional[int] = None,
    economia_atacante: Optional[EconomiaTurno] = None,
    alvo_desengajado: bool = False,
) -> Dict[str, Any]:
    """Resolve ataque de oportunidade e consome reação do atacante."""
    eco = economia_atacante or EconomiaTurno()
    validar_oportunidade(eco, alvo_desengajado=alvo_desengajado)
    resultado = resolver_ataque_com_arma(
        arma_slug=arma_slug,
        str_mod=str_mod,
        dex_mod=dex_mod,
        bonus_proficiencia=bonus_proficiencia,
        ac_alvo=ac_alvo,
        rolagem_d20=rolagem_d20,
        proficiente=True,
        feats=feats,
        corpo_a_corpo=True,
        raca_slug=raca_slug,
    )
    nova_eco = gastar_acao_turno(eco, "reacao")
    resultado["economia_atacante"] = nova_eco.as_dict()
    resultado["tipo"] = "ataque_oportunidade"
    return resultado
