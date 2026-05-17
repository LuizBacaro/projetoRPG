"""
Regras de companheiro animal D&D 3.5 (PHB).
Fonte: .cursor/requisitos/dnd35/09-companheiro-animal-dnd35.md
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

_CLASSE_ALIASES = {
    "druida": "Druida",
    "druid": "Druida",
    "ranger": "Ranger",
    "patrulheiro": "Ranger",
}

# Truques e habilidades especiais usam tiers; HD e AN usam fórmulas (§ Referência Rápida)
_TRUQUES_BONUS_LIMITES = (
    (1, 1),
    (4, 2),
    (7, 3),
    (10, 4),
    (13, 5),
    (16, 6),
    (19, 7),
)
_HABILIDADES_ESPECIAIS = (
    (1, ("link", "vinculo_compartilhado")),
    (3, ("compreensao_linguagem",)),
    (5, ("telepatia",)),
    (7, ("sentidos_agucados",)),
    (9, ("compreensao_idiomas",)),
    (11, ("falar_idioma",)),
    (13, ("inumanidade",)),
    (15, ("comunhao_distante",)),
)


def _tier(nivel_efetivo: int) -> int:
    n = max(0, int(nivel_efetivo))
    if n <= 2:
        return 0
    if n <= 5:
        return 1
    if n <= 8:
        return 2
    if n <= 11:
        return 3
    if n <= 14:
        return 4
    if n <= 17:
        return 5
    return 6


def modificar_atributo(valor: int) -> int:
    return (int(valor) - 10) // 2


def _nivel_na_parte(texto: str) -> Optional[int]:
    m = re.search(r"(\d+)", texto)
    return int(m.group(1)) if m else None


def _classe_na_parte(parte: str) -> Tuple[Optional[str], Optional[int]]:
    p = (parte or "").strip()
    if not p:
        return None, None
    low = p.lower()
    for alias, canon in _CLASSE_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", low):
            nv = _nivel_na_parte(p)
            return canon, nv
    return None, None


def resolver_classe_companheiro(
    classe: str | None, nivel_personagem: int
) -> Tuple[Optional[str], int]:
    """
    Identifica Druida ou Ranger em strings simples ou multiclasse
    (ex.: 'Druida', 'Druida 7', 'Guerreiro 5 / Druida 7').
    Retorna (classe_canonica, nivel_da_classe).
    """
    if not classe:
        return None, 0
    s = str(classe).strip()
    if not s:
        return None, 0
    n_total = max(1, int(nivel_personagem or 1))
    low = s.lower()
    if low in _CLASSE_ALIASES:
        return _CLASSE_ALIASES[low], n_total

    encontrados: List[Tuple[str, int]] = []
    for parte in re.split(r"[/,;|]+", s):
        tipo, nv = _classe_na_parte(parte)
        if tipo:
            encontrados.append((tipo, nv if nv is not None else n_total))

    if not encontrados:
        tipo, nv = _classe_na_parte(s)
        if tipo:
            encontrados.append((tipo, nv if nv is not None else n_total))

    if not encontrados:
        return None, 0

    druidas = [n for t, n in encontrados if t == "Druida"]
    if druidas:
        return "Druida", max(druidas)
    rangers = [n for t, n in encontrados if t == "Ranger"]
    if rangers:
        return "Ranger", max(rangers)
    return None, 0


def normalizar_classe(classe: str | None) -> str:
    canon, _ = resolver_classe_companheiro(classe, 1)
    if canon:
        return canon
    return str(classe or "").strip()


def elegibilidade_companheiro(classe: str | None, nivel: int) -> Tuple[bool, str, int]:
    """
    Retorna (elegivel, motivo, nivel_efetivo).
    """
    c, n_classe = resolver_classe_companheiro(classe, nivel)
    if c == "Druida":
        return True, "", n_classe
    if c == "Ranger":
        if n_classe < 4:
            return False, "Ranger obtém companheiro animal no 4º nível.", 0
        return True, "", n_classe - 3
    motivo = (
        "Apenas Druida (1º nível) ou Ranger (4º nível) podem ter companheiro animal."
    )
    if classe and str(classe).strip():
        motivo = f"{motivo} (classe no cadastro: {str(classe).strip()})"
    return False, motivo, 0


def hd_bonus(nivel_efetivo: int) -> int:
    """HD bônus = floor(nível efetivo / 3) — ver exemplo Druida 7 no requisito §15."""
    n = max(0, int(nivel_efetivo))
    return n // 3


def armadura_natural_bonus(nivel_efetivo: int) -> int:
    """Bônus AN = floor(nível efetivo / 3) + 1."""
    n = max(0, int(nivel_efetivo))
    return n // 3 + 1


def truques_bonus_qtd(nivel_efetivo: int) -> int:
    n = max(0, int(nivel_efetivo))
    qtd = 0
    for limite, valor in _TRUQUES_BONUS_LIMITES:
        if n >= limite:
            qtd = valor
    return qtd


def talentos_total(hd_total: int) -> int:
    h = max(1, int(hd_total))
    return 1 + max(0, (h - 1) // 3)


def salvamentos(hd_total: int) -> Dict[str, int]:
    h = max(1, int(hd_total))
    return {
        "fortitude": 2 + h // 2,
        "reflexos": 2 + h // 2,
        "vontade": 1 + h // 3,
    }


def distribuicao_atributos_resumo(nivel_efetivo: int) -> str:
    """Texto orientativo para UI (escolhas do jogador)."""
    n = max(0, int(nivel_efetivo))
    if n <= 2:
        return "+2 em um atributo à escolha"
    if n <= 5:
        return "+2 em dois atributos à escolha"
    if n <= 8:
        return "+3 em dois atributos e +2 em um atributo"
    return "+3 em três atributos à escolha"


def habilidades_especiais_ativas(nivel_efetivo: int) -> List[str]:
    n = max(0, int(nivel_efetivo))
    out: List[str] = []
    for limite, slugs in _HABILIDADES_ESPECIAIS:
        if n >= limite:
            for s in slugs:
                if s not in out:
                    out.append(s)
    return out


def calcular_estatisticas(
    *,
    nivel_efetivo: int,
    hd_base: int,
    atributos_base: Dict[str, int],
    bonus_atributos: Optional[Dict[str, int]] = None,
    armadura_natural_base: int = 0,
) -> Dict[str, Any]:
    """Calcula bloco derivado para API/UI."""
    bonus = bonus_atributos or {}
    attrs = {
        k: int(atributos_base.get(k, 10)) + int(bonus.get(k, 0))
        for k in (
            "forca",
            "destreza",
            "constituicao",
            "inteligencia",
            "sabedoria",
            "carisma",
        )
    }
    hd_b = hd_bonus(nivel_efetivo)
    hd_total = max(1, int(hd_base) + hd_b)
    an_vinculo = armadura_natural_bonus(nivel_efetivo)
    an_total = int(armadura_natural_base) + an_vinculo
    con_mod = modificar_atributo(attrs["constituicao"])
    des_mod = modificar_atributo(attrs["destreza"])
    hp_max = max(1, hd_total * max(1, 5 + con_mod))
    saves = salvamentos(hd_total)
    return {
        "nivel_efetivo": nivel_efetivo,
        "hd_bonus": hd_b,
        "hd_total": hd_total,
        "atributos_efetivos": attrs,
        "modificadores": {k: modificar_atributo(v) for k, v in attrs.items()},
        "bab": hd_total,
        "fortitude": saves["fortitude"],
        "reflexos": saves["reflexos"],
        "vontade": saves["vontade"],
        "armadura_natural_base": armadura_natural_base,
        "armadura_natural_vinculo": an_vinculo,
        "armadura_natural_total": an_total,
        "ca": 10 + an_total + des_mod,
        "hp_max_sugerido": hp_max,
        "talentos_total": talentos_total(hd_total),
        "truques_bonus": truques_bonus_qtd(nivel_efetivo),
        "distribuicao_atributos": distribuicao_atributos_resumo(nivel_efetivo),
        "habilidades_especiais": habilidades_especiais_ativas(nivel_efetivo),
    }
