"""Traits raciais D&D 5E aplicáveis em combate (primeira leva PHB)."""

from __future__ import annotations

import random
from typing import Callable, List, Optional, Sequence, Tuple

from app.games.dnd5e.rules.combate import rolar_d20_ataque
from app.games.dnd5e.rules.raca_variantes import tipo_dano_resistencia_racial
from app.games.dnd5e.rules.racas import raca_por_slug

CATEGORIAS_VENENO = frozenset({"veneno", "poison"})
CATEGORIAS_ENCANTAMENTO = frozenset({"encantamento", "charm", "enchantment"})
CONDICOES_ENCANTAMENTO = frozenset({"enfeiticado", "charmed"})


def _caracteristicas(raca_slug: str) -> List[str]:
    raca = raca_por_slug(raca_slug)
    if not raca:
        return []
    return list(raca.get("caracteristicas") or [])


def vantagem_salvamento_racial(
    raca_slug: str,
    *,
    categoria: str = "",
    condicoes: Optional[Sequence[str]] = None,
) -> bool:
    """Elfo: vantagem em salvamentos contra encantamento."""
    if "vantagem_encantamento" not in _caracteristicas(raca_slug):
        return False
    cat = (categoria or "").strip().lower()
    if cat in CATEGORIAS_ENCANTAMENTO:
        return True
    slugs = {str(c).strip().lower() for c in (condicoes or [])}
    return bool(slugs & CONDICOES_ENCANTAMENTO)


def bonus_salvamento_racial(raca_slug: str, *, categoria: str = "") -> int:
    """Anão: +2 em salvamentos contra veneno."""
    if "resistencia_veneno" not in _caracteristicas(raca_slug):
        return 0
    cat = (categoria or "").strip().lower()
    if cat in CATEGORIAS_VENENO:
        return 2
    return 0


def _tipos_equivalentes(tipo: str) -> set[str]:
    t = (tipo or "").strip().lower()
    mapa = {
        "acid": "acido",
        "poison": "veneno",
        "fire": "fogo",
        "cold": "frio",
        "lightning": "eletricidade",
    }
    canon = mapa.get(t, t)
    rev = {canon}
    for k, v in mapa.items():
        if v == canon:
            rev.add(k)
    return rev


def reduzir_dano_racial(
    raca_slug: str,
    dano: int,
    tipo_dano: str = "",
    *,
    raca_variante_slug: str = "",
) -> Tuple[int, str]:
    """Anão: veneno; draconato/tiefling: tipo da linhagem (metade)."""
    tipo = (tipo_dano or "").strip().lower()
    tipos_alvo = _tipos_equivalentes(tipo)

    if "resistencia_veneno" in _caracteristicas(raca_slug):
        if tipos_alvo & CATEGORIAS_VENENO or tipo in CATEGORIAS_VENENO:
            novo = max(0, int(dano) // 2)
            if novo != dano:
                return novo, f"Resistência anã (veneno): {dano} → {novo}"

    resistencia = tipo_dano_resistencia_racial(raca_slug, raca_variante_slug or None)
    if resistencia and tipos_alvo & _tipos_equivalentes(resistencia):
        novo = max(0, int(dano) // 2)
        if novo != dano:
            label = raca_variante_slug or raca_slug
            return novo, f"Resistência racial ({label}): {dano} → {novo}"

    return dano, ""


def aplicar_sorte_halfling(
    roll: int,
    *,
    raca_slug: str,
    aplicar: bool = True,
    rng: Optional[Callable[[int, int], int]] = None,
) -> Tuple[int, Optional[int]]:
    """Halfling: rerrolar natural 1 em teste d20."""
    if not aplicar or roll != 1:
        return roll, None
    if "sorte" not in _caracteristicas(raca_slug):
        return roll, None
    reroll = rng(1, 20) if rng else random.randint(1, 20)
    return reroll, reroll


def resolver_salvamento_racial(
    mod_atributo: int,
    bonus_proficiencia: int,
    cd: int,
    *,
    proficiente: bool = False,
    raca_slug: str = "",
    categoria: str = "",
    condicoes: Optional[Sequence[str]] = None,
    rolagem_d20: Optional[int] = None,
    aplicar_sorte_halfling_flag: bool = True,
    rng: Optional[Callable[[int, int], int]] = None,
) -> dict:
    """Salvaguarda d20 + mod + prof + bônus racial; traits elfo/anão/halfling."""
    vant = vantagem_salvamento_racial(
        raca_slug, categoria=categoria, condicoes=condicoes
    )
    bonus_racial = bonus_salvamento_racial(raca_slug, categoria=categoria)
    roll, roll2 = rolar_d20_ataque(
        vantagem=vant,
        desvantagem=False,
        rolagem_forcada=rolagem_d20,
        rng=rng,
    )
    sorte_roll = None
    if rolagem_d20 is None:
        roll, sorte_roll = aplicar_sorte_halfling(
            roll,
            raca_slug=raca_slug,
            aplicar=aplicar_sorte_halfling_flag,
            rng=rng,
        )
    prof = bonus_proficiencia if proficiente else 0
    total = roll + mod_atributo + prof + bonus_racial
    return {
        "rolagem": roll,
        "rolagem_secundaria": roll2,
        "sorte_reroll": sorte_roll,
        "total": total,
        "sucesso": total >= cd,
        "vantagem": vant,
        "bonus_racial": bonus_racial,
        "cd": cd,
    }


def resolver_ataque_com_raca(
    mod_atributo: int,
    bonus_proficiencia: int,
    ac_alvo: int,
    *,
    rolagem_d20: Optional[int] = None,
    proficiente: bool = True,
    bonus_extra: int = 0,
    condicoes_atacante: Optional[Sequence[str]] = None,
    condicoes_alvo: Optional[Sequence[str]] = None,
    corpo_a_corpo: bool = True,
    raca_slug: str = "",
    aplicar_sorte_halfling_flag: bool = True,
    rng: Optional[Callable[[int, int], int]] = None,
) -> dict:
    """Ataque d20 com traits raciais (sorte halfling)."""
    from app.games.dnd5e.rules.combate import (
        ResultadoAtaque,
        resumo_modificadores_ataque,
    )

    mods = resumo_modificadores_ataque(
        condicoes_atacante,
        condicoes_alvo,
        corpo_a_corpo=corpo_a_corpo,
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
    total = roll + mod_atributo + prof + bonus_extra
    if mods.acerto_automatico:
        acerto = True
    else:
        acerto = total >= ac_alvo or roll == 20
    is_critico = mods.critico_automatico or roll == 20
    resultado = ResultadoAtaque(
        rolagem=roll,
        rolagem_secundaria=roll2,
        total=total,
        acerto=acerto,
        vantagem=vant,
        desvantagem=desv,
        critico_automatico=mods.critico_automatico,
        acerto_automatico=mods.acerto_automatico,
        is_critico=is_critico,
    )
    out = {
        "rolagem": resultado.rolagem,
        "rolagem_secundaria": resultado.rolagem_secundaria,
        "total": resultado.total,
        "acerto": resultado.acerto,
        "vantagem": resultado.vantagem,
        "desvantagem": resultado.desvantagem,
        "critico_automatico": resultado.critico_automatico,
        "acerto_automatico": resultado.acerto_automatico,
        "is_critico": resultado.is_critico,
        "sorte_reroll": sorte_reroll,
    }
    return out
