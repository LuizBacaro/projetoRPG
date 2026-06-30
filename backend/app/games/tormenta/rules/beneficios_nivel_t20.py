"""Benefícios globais por nível — XP, graduação de perícias, poderes gerais, PH e meio-nível."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_MB,
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_BEN_MB_JSON = _DATA_DIR / "beneficios_nivel_mb.json"
_BEN_V13_JSON = _DATA_DIR / "beneficios_nivel_v13.json"


@lru_cache(maxsize=2)
def _carregar_beneficios_raw(
    regra_versao: str = REGRA_VERSAO_MB,
) -> List[Dict[str, Any]]:
    path = (
        _BEN_V13_JSON
        if normalizar_regra_versao(regra_versao) == REGRA_VERSAO_V13
        else _BEN_MB_JSON
    )
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("niveis") or []
    return rows if isinstance(rows, list) else []


def _normalizar_linha_beneficio(
    row: Dict[str, Any], regra_versao: str
) -> Optional[Dict[str, Any]]:
    if not isinstance(row, dict):
        return None
    try:
        n = int(row.get("nivel", 0))
    except (TypeError, ValueError):
        return None
    if n < 1 or n > 40:
        return None
    rv = normalizar_regra_versao(regra_versao)
    talentos_raw = row.get("poderes_gerais_totais")
    if talentos_raw is None:
        talentos_raw = row.get("talentos_totais", 0)
    out: Dict[str, Any] = {
        "nivel": n,
        "xp_total": int(row.get("xp_total", 0) or 0),
        "graduacao_pericias": str(row.get("graduacao_pericias", "") or "").strip(),
        "talentos_totais": int(talentos_raw or 0),
        "pontos_habilidade_acumulados": int(
            row.get("pontos_habilidade_acumulados", 0) or 0
        ),
        "bonus_meio_nivel": int(row.get("bonus_meio_nivel", 0) or 0),
    }
    if rv == REGRA_VERSAO_V13:
        out["poderes_gerais_totais"] = out["talentos_totais"]
    return out


def lista_beneficios_por_nivel(
    regra_versao: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Tabela «Benefícios por Nível» conforme edição (MB ou v1.3)."""
    rv = normalizar_regra_versao(regra_versao)
    out: List[Dict[str, Any]] = []
    for row in _carregar_beneficios_raw(rv):
        parsed = _normalizar_linha_beneficio(row, rv)
        if parsed:
            out.append(parsed)
    return sorted(out, key=lambda x: x["nivel"])


def lista_beneficios_por_nivel_mb() -> List[Dict[str, Any]]:
    """Compatibilidade — benefícios MB."""
    return lista_beneficios_por_nivel(REGRA_VERSAO_MB)


def beneficio_nivel(
    nivel: int, regra_versao: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    try:
        nv = int(nivel)
    except (TypeError, ValueError):
        nv = 1
    for row in lista_beneficios_por_nivel(regra_versao):
        if int(row.get("nivel", 0)) == nv:
            return row
    return None


def beneficio_nivel_mb(nivel: int) -> Optional[Dict[str, Any]]:
    return beneficio_nivel(nivel, REGRA_VERSAO_MB)


def graduacao_pericias_texto_v13(nivel: int) -> str:
    """Referência ⌊nível/2⌋ + bônus de treino (+2 / +4 / +6) — deve bater com o JSON v1.3."""
    from app.games.tormenta.rules.pericias_t20 import bonus_treinamento_por_nivel

    try:
        nv = max(1, min(40, int(nivel)))
    except (TypeError, ValueError):
        nv = 1
    meio = nv // 2
    treino = bonus_treinamento_por_nivel(nv, REGRA_VERSAO_V13)
    return f"+{meio + treino}/+{meio}"
