"""Tabela de dano por ST (GURPS 4e/Lite): thr (golpe de ponta) e sw (balanço)."""

from __future__ import annotations

from typing import Tuple

# Faixa prática da tabela para a ficha Lite no Arena.
_ST_DAMAGE_TABLE: dict[int, Tuple[str, str]] = {
    1: ("1d-6", "1d-5"),
    2: ("1d-6", "1d-5"),
    3: ("1d-5", "1d-4"),
    4: ("1d-5", "1d-4"),
    5: ("1d-4", "1d-3"),
    6: ("1d-4", "1d-3"),
    7: ("1d-3", "1d-2"),
    8: ("1d-3", "1d-2"),
    9: ("1d-2", "1d-1"),
    10: ("1d-2", "1d"),
    11: ("1d-1", "1d+1"),
    12: ("1d-1", "1d+2"),
    13: ("1d", "2d-1"),
    14: ("1d", "2d"),
    15: ("1d+1", "2d+1"),
    16: ("1d+1", "2d+2"),
    17: ("1d+2", "3d-1"),
    18: ("1d+2", "3d"),
    19: ("2d-1", "3d+1"),
    20: ("2d-1", "3d+2"),
    21: ("2d", "4d-1"),
    22: ("2d", "4d"),
    23: ("2d+1", "4d+1"),
    24: ("2d+1", "4d+2"),
    25: ("2d+2", "5d-1"),
    26: ("2d+2", "5d"),
    27: ("3d-1", "5d+1"),
    28: ("3d-1", "5d+1"),
    29: ("3d", "5d+2"),
    30: ("3d", "6d-1"),
}


def dano_thr_sw_por_st(st_valor: int) -> Tuple[str, str]:
    """Retorna (thr, sw) para ST; fora da faixa usa o limite mais próximo."""
    st = int(st_valor or 0)
    if st <= 1:
        return _ST_DAMAGE_TABLE[1]
    if st >= 30:
        return _ST_DAMAGE_TABLE[30]
    return _ST_DAMAGE_TABLE[st]

