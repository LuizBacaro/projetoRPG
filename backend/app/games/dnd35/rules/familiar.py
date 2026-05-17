"""
Regras de familiar D&D 3.5 (PHB) — Mago e Feiticeiro.
Fonte: .cursor/requisitos/dnd35/10-familiar-dnd35.md
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

_FAMILIAR_ALIASES = {
    "mago": "Mago",
    "wizard": "Mago",
    "feiticeiro": "Feiticeiro",
    "sorcerer": "Feiticeiro",
    "sorceror": "Feiticeiro",
}

_PROGRESSAO: List[Tuple[int, int, int, List[str]]] = [
    (
        2,
        1,
        6,
        ["prontidao", "evasao_aprimorada", "partilhar_magias", "vinculo_empatico"],
    ),
    (4, 2, 7, ["transmitir_magias_toque"]),
    (6, 3, 8, ["falar_com_mestre"]),
    (8, 4, 9, ["falar_animais_especie"]),
    (10, 5, 10, []),
    (12, 6, 11, ["resistencia_magia"]),
    (14, 7, 12, ["videncia_familiar"]),
    (16, 8, 13, []),
    (18, 9, 14, []),
    (20, 10, 15, []),
]


def modificar_atributo(valor: int) -> int:
    return (int(valor) - 10) // 2


def _nivel_na_parte(texto: str) -> Optional[int]:
    m = re.search(r"(\d+)", texto)
    return int(m.group(1)) if m else None


def _classe_familiar_na_parte(parte: str) -> Tuple[Optional[str], Optional[int]]:
    p = (parte or "").strip()
    if not p:
        return None, None
    low = p.lower()
    for alias, canon in _FAMILIAR_ALIASES.items():
        if re.search(rf"\b{re.escape(alias)}\b", low):
            return canon, _nivel_na_parte(p)
    return None, None


def niveis_familiar_classe(classe: str | None, nivel_personagem: int) -> int:
    """
    Soma níveis de Mago + Feiticeiro em string de classe (multiclasse).
    """
    if not classe:
        return 0
    s = str(classe).strip()
    if not s:
        return 0
    n_total = max(1, int(nivel_personagem or 1))
    total = 0
    for parte in re.split(r"[/,;|]+", s):
        tipo, nv = _classe_familiar_na_parte(parte)
        if tipo:
            total += nv if nv is not None else 0
    if total > 0:
        return total
    tipo, nv = _classe_familiar_na_parte(s)
    if tipo:
        return nv if nv is not None else n_total
    low = s.lower()
    if low in _FAMILIAR_ALIASES:
        return n_total
    return 0


def elegibilidade_familiar(classe: str | None, nivel: int) -> Tuple[bool, str, int]:
    """Retorna (elegivel, motivo, nivel_mestre_familiar)."""
    n_mestre = niveis_familiar_classe(classe, nivel)
    if n_mestre >= 1:
        return True, "", n_mestre
    motivo = (
        "Apenas Mago ou Feiticeiro podem ter familiar (PHB). "
        "Druida e Ranger usam companheiro animal."
    )
    if classe and str(classe).strip():
        motivo = f"{motivo} (classe no cadastro: {str(classe).strip()})"
    return False, motivo, 0


def linha_progressao(nivel_mestre: int) -> Dict[str, Any]:
    n = max(1, int(nivel_mestre))
    an = 1
    intel = 6
    habilidades: List[str] = []
    for limite, an_b, int_b, habs in _PROGRESSAO:
        if n <= limite:
            an = an_b
            intel = int_b
            habilidades = list(habs)
            break
    else:
        an, intel, habilidades = (
            _PROGRESSAO[-1][1],
            _PROGRESSAO[-1][2],
            list(_PROGRESSAO[-1][3]),
        )
    return {
        "nivel_mestre": n,
        "armadura_natural_bonus": an,
        "inteligencia": intel,
        "habilidades_especiais": habilidades,
        "resistencia_magia": n + 5 if n >= 11 else None,
    }


def calcular_derivadas_familiar(
    *,
    nivel_mestre: int,
    hp_maximo_mestre: int,
    atributos_base: Dict[str, int],
    armadura_natural_base: int = 0,
    hp_extra_mestre: int = 0,
) -> Dict[str, Any]:
    prog = linha_progressao(nivel_mestre)
    des = int(atributos_base.get("destreza", 10))
    des_mod = modificar_atributo(des)
    an_total = int(armadura_natural_base) + int(prog["armadura_natural_bonus"])
    hp_base = max(1, int(hp_maximo_mestre) // 2)
    hp_max = hp_base + int(hp_extra_mestre or 0)
    return {
        **prog,
        "atributos_base": dict(atributos_base),
        "modificadores": {k: modificar_atributo(v) for k, v in atributos_base.items()},
        "armadura_natural_base": int(armadura_natural_base),
        "armadura_natural_total": an_total,
        "ca": 10 + an_total + des_mod,
        "hp_max_sugerido": hp_max,
        "hp_extra_mestre": int(hp_extra_mestre or 0),
    }
