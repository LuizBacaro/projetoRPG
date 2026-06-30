"""Penalidade de armadura em perícias — Tormenta 20 v1.3 (RF-T07e / RF-T04d)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional


def penalidade_equipada_total(itens_protecao: Optional[List[Any]]) -> int:
    """
    Soma magnitudes negativas de penalidade de armadura + escudo equipados.
    Ex.: couro reforçado (−1) + escudo leve (−1) → 2.
    """
    total = 0
    for it in itens_protecao or []:
        if not isinstance(it, dict):
            continue
        try:
            pen = int(it.get("penalidade", 0) or 0)
        except (TypeError, ValueError):
            pen = 0
        if pen < 0:
            total += abs(pen)
    return total


def pericia_aplica_penalidade_armadura(
    meta: Optional[Dict[str, Any]],
    *,
    uso_atletismo_natacao: bool = False,
) -> bool:
    """Tabela 2-1 (A) + exceção Atletismo só em natação (p.116)."""
    if not meta:
        return False
    if meta.get("penalidade_armadura"):
        return True
    if meta.get("penalidade_armadura_natacao") and uso_atletismo_natacao:
        return True
    return False


def penalidade_armadura_pericia(
    meta: Optional[Dict[str, Any]],
    itens_protecao: Optional[List[Any]],
    *,
    uso_atletismo_natacao: bool = False,
) -> int:
    """Valor positivo a subtrair do bônus (0 se a perícia não sofre penalidade)."""
    if not pericia_aplica_penalidade_armadura(
        meta, uso_atletismo_natacao=uso_atletismo_natacao
    ):
        return 0
    return penalidade_equipada_total(itens_protecao)
