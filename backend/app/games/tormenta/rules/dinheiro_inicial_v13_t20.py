"""Dinheiro inicial v1.3 — Tabela 3-1 (níveis 2–20) e 4d6 no 1º nível."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Union

from app.games.tormenta.rules.regra_versao_t20 import REGRA_VERSAO_V13

_DATA_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "dinheiro_inicial_v13.json"
)


@lru_cache(maxsize=1)
def _carregar_tabela() -> Dict[str, Union[str, int]]:
    raw = json.loads(_DATA_PATH.read_text(encoding="utf-8"))
    por = raw.get("por_nivel") or {}
    return {str(k): v for k, v in por.items()}


def dinheiro_por_nivel(nivel: int) -> Dict[str, Any]:
    """
    Retorna tipo e valor do dinheiro inicial para o nível informado.

    Nível 1 → ``{"tipo": "4d6", "valor": None}``; demais → ``{"tipo": "fixo", "valor": int}``.
    """
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    nv = max(1, min(20, nv))
    tabela = _carregar_tabela()
    entry = tabela.get(str(nv))
    if entry == "4d6" or nv == 1:
        return {"nivel": nv, "tipo": "4d6", "valor": None, "tabela_ref": "Tabela 3-1"}
    if isinstance(entry, int):
        return {"nivel": nv, "tipo": "fixo", "valor": entry, "tabela_ref": "Tabela 3-1"}
    return {"nivel": nv, "tipo": "4d6", "valor": None, "tabela_ref": "Tabela 3-1"}


def preview_dinheiro_inicial_v13(nivel: int) -> Dict[str, Any]:
    data = dinheiro_por_nivel(nivel)
    return {**data, "regra_versao": REGRA_VERSAO_V13}
