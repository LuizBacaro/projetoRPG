"""Penalidade de armadura em perícias — Tormenta 20 v1.3 (RF-T07e / RF-T04d / RF-T07e-1)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.proficiencia_armadura_t20 import (
    tem_protecao_sem_proficiencia,
)


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
    nao_proficiente_armadura: bool = False,
) -> bool:
    """
    Tabela 2-1 (A) + exceção Atletismo só em natação (p.116).
    RF-T07e-1: sem proficiência → **todas** perícias For/Des (Atletismo sempre).
    """
    if not meta:
        return False
    if nao_proficiente_armadura:
        attr = str(meta.get("atributo") or "").strip().lower()
        if attr in ("for", "des"):
            return True
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
    slug_classe: Optional[str] = None,
    nao_proficiente_armadura: Optional[bool] = None,
) -> int:
    """Valor positivo a subtrair do bônus (0 se a perícia não sofre penalidade)."""
    if nao_proficiente_armadura is None:
        nao_proficiente_armadura = tem_protecao_sem_proficiencia(
            itens_protecao, slug_classe
        )
    if not pericia_aplica_penalidade_armadura(
        meta,
        uso_atletismo_natacao=uso_atletismo_natacao,
        nao_proficiente_armadura=nao_proficiente_armadura,
    ):
        return 0
    return penalidade_equipada_total(itens_protecao)
