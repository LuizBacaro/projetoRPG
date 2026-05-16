"""Progressão MB de magias por classe — tipo de lista (arcana/divina) e círculo máximo lançável.

Valores alinhados a `classes_mb.json` / Módulo Básico (Cap. magia + Cap. 3). Paladino e ranger usam
nível mínimo de conjuração em `conjuracao_classe_mb.json` (5) e progressão de meio-conjurador no MB.
"""

from __future__ import annotations

from typing import Literal, Optional

from app.games.tormenta.rules.conjuracao_t20 import _mapa_conjuracao_por_slug

TipoListaMb = Literal["arcana", "divina"]


def tipo_lista_magias_por_classe_mb(slug_classe: str) -> Optional[TipoListaMb]:
    """Tipo de magias do catálogo MB associado à classe conjuradora, ou None se não houver lista MB."""
    s = str(slug_classe or "").strip().lower()
    if s in ("mago", "bardo", "feiticeiro"):
        return "arcana"
    if s in ("clerigo", "druida", "paladino", "ranger"):
        return "divina"
    return None


def circulo_maximo_magias_lancaveis_mb(slug_classe: str, nivel: int) -> int:
    """
    Maior círculo de magia lançável (1–9) conforme nível da classe; 0 = só truques (círculo 0) ou
    nível abaixo do início de conjuração da classe.
    """
    s = str(slug_classe or "").strip().lower()
    try:
        n = int(nivel)
    except (TypeError, ValueError):
        n = 1
    n = max(1, min(40, n))

    row = _mapa_conjuracao_por_slug().get(s)
    if not row:
        return 0
    ini = int(row.get("conjuracao_inicia_nivel", 1) or 1)
    if n < ini:
        return 0

    if s in ("clerigo", "druida", "feiticeiro"):
        return min(9, (n + 1) // 2)
    if s == "mago":
        return min(9, (n + 2) // 2)
    if s == "bardo":
        return min(6, 1 + (n - 1) // 3)
    if s in ("paladino", "ranger"):
        return min(4, 1 + (n - ini) // 4)
    return min(9, (n + 1) // 2)
