"""Propriedades de arma PHB — finesse, versátil, leve, duas mãos (ataque e dano)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from app.games.dnd5e.rules.combate import calcular_dano, rolar_d20_ataque
from app.games.dnd5e.rules.equipamento import Arma, arma_por_slug
from app.games.dnd5e.rules.feat_efeitos import bonus_ataque_feats
from app.games.dnd5e.rules.raca_traits import aplicar_sorte_halfling


def _tem_propriedade(arma: Arma, prop: str) -> bool:
    return prop in {p.lower() for p in (arma.propriedades or [])}


def mod_atributo_para_arma(
    arma: Optional[Arma],
    *,
    str_mod: int,
    dex_mod: int,
    corpo_a_corpo: bool = True,
) -> Tuple[int, str]:
    """Retorna (mod usado, atributo escolhido)."""
    if arma is None:
        mod = dex_mod if not corpo_a_corpo else str_mod
        attr = "dexterity" if not corpo_a_corpo else "strength"
        return mod, attr

    if _tem_propriedade(arma, "finesse"):
        if str_mod >= dex_mod:
            return str_mod, "strength"
        return dex_mod, "dexterity"

    if arma.tipo == "distancia" or not corpo_a_corpo:
        return dex_mod, "dexterity"

    return str_mod, "strength"


def expressao_dano_arma(
    arma: Optional[Arma],
    *,
    duas_maos: bool = False,
    dano_override: Optional[str] = None,
) -> str:
    if dano_override:
        return dano_override
    if arma is None:
        return "1d4"
    if duas_maos and _tem_propriedade(arma, "versatil"):
        return str(getattr(arma, "dano_versatil", None) or arma.dano)
    return arma.dano


def propriedades_resumo(arma_slug: Optional[str]) -> List[str]:
    arma = arma_por_slug(arma_slug)
    if not arma:
        return []
    return list(arma.propriedades or [])


def resolver_ataque_com_arma(
    *,
    arma_slug: Optional[str],
    str_mod: int,
    dex_mod: int,
    bonus_proficiencia: int,
    ac_alvo: int,
    rolagem_d20: Optional[int] = None,
    proficiente: bool = True,
    bonus_extra: int = 0,
    feats: Optional[List[str]] = None,
    duas_maos: bool = False,
    corpo_a_corpo: Optional[bool] = None,
    condicoes_atacante: Optional[List[str]] = None,
    condicoes_alvo: Optional[List[str]] = None,
    raca_slug: str = "",
    aplicar_sorte_halfling_flag: bool = True,
    rng=None,
) -> Dict[str, Any]:
    """Resolve ataque usando propriedades da arma e bônus de feats."""
    arma = arma_por_slug(arma_slug)
    cac = (
        corpo_a_corpo
        if corpo_a_corpo is not None
        else (arma is None or arma.tipo != "distancia")
    )
    mod_attr, attr_usado = mod_atributo_para_arma(
        arma, str_mod=str_mod, dex_mod=dex_mod, corpo_a_corpo=cac
    )
    distancia = not cac or (arma is not None and arma.tipo == "distancia")
    bonus_feats = bonus_ataque_feats(
        feats,
        corpo_a_corpo=cac,
        distancia=distancia,
        bonus_extra_manual=bonus_extra,
    )
    from app.games.dnd5e.rules.combate import resumo_modificadores_ataque

    mods = resumo_modificadores_ataque(
        condicoes_atacante,
        condicoes_alvo,
        corpo_a_corpo=cac,
    )
    vant, desv = mods.rolagem_efetiva()
    roll, roll2 = rolar_d20_ataque(
        vantagem=vant,
        desvantagem=desv,
        rolagem_forcada=rolagem_d20,
        rng=rng,
    )
    sorte_reroll = None
    if rolagem_d20 is None:
        roll, sorte_reroll = aplicar_sorte_halfling(
            roll,
            raca_slug=raca_slug,
            aplicar=aplicar_sorte_halfling_flag,
            rng=rng,
        )
    prof = bonus_proficiencia if proficiente else 0
    total = roll + mod_attr + prof + bonus_feats
    if mods.acerto_automatico:
        acerto = True
    else:
        acerto = total >= ac_alvo or roll == 20
    is_critico = mods.critico_automatico or roll == 20
    props = list(arma.propriedades) if arma else []
    if duas_maos and _tem_propriedade(arma, "versatil") if arma else False:
        props = props + ["versatil_duas_maos"]
    return {
        "rolagem": roll,
        "rolagem_secundaria": roll2,
        "total": total,
        "acerto": acerto,
        "vantagem": vant,
        "desvantagem": desv,
        "critico_automatico": mods.critico_automatico,
        "acerto_automatico": mods.acerto_automatico,
        "is_critico": is_critico,
        "sorte_reroll": sorte_reroll,
        "mod_atributo_usado": mod_attr,
        "atributo_usado": attr_usado,
        "arma_slug": arma_slug,
        "propriedades": props,
        "corpo_a_corpo": cac,
        "duas_maos": duas_maos,
        "bonus_feats": bonus_feats - bonus_extra,
    }


def calcular_dano_com_arma(
    *,
    arma_slug: Optional[str],
    str_mod: int,
    dex_mod: int,
    is_critico: bool = False,
    duas_maos: bool = False,
    dano_override: Optional[str] = None,
    mod_override: Optional[int] = None,
    rng=None,
) -> Dict[str, Any]:
    arma = arma_por_slug(arma_slug)
    mod_attr, attr_usado = mod_atributo_para_arma(
        arma, str_mod=str_mod, dex_mod=dex_mod, corpo_a_corpo=True
    )
    if mod_override is not None:
        mod_attr = int(mod_override)
    expressao = expressao_dano_arma(
        arma, duas_maos=duas_maos, dano_override=dano_override
    )
    from app.games.dnd5e.rules.combate import ArmaCombate

    total = calcular_dano(ArmaCombate(dano=expressao), mod_attr, is_critico, rng=rng)
    return {
        "dano_total": total,
        "expressao_dano": expressao,
        "mod_atributo_usado": mod_attr,
        "atributo_usado": attr_usado,
        "is_critico": is_critico,
        "duas_maos": duas_maos,
    }
