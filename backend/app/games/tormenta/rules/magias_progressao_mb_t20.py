"""Progressão MB de magias por classe — tipo de lista (arcana/divina) e círculo máximo lançável.

Valores alinhados a `classes_mb.json` / Módulo Básico (Cap. magia + Cap. 3). Paladino e ranger usam
nível mínimo de conjuração em `conjuracao_classe_mb.json` (5) e progressão de meio-conjurador no MB.
v1.3: arcanista delega às tabelas MB via caminho; caçador usa ranger.
"""

from __future__ import annotations

from typing import Literal, Optional

from app.games.tormenta.rules.conjuracao_t20 import (
    _mapa_conjuracao_por_slug,
    mapa_conjuracao_por_slug,
)
from app.games.tormenta.rules.grimorio_conjuracao_t20 import (
    slug_efetivo_tabelas_magia_mb,
)
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    normalizar_regra_versao,
)

TipoListaMb = Literal["arcana", "divina"]


def tipo_lista_magias_por_classe_mb(slug_classe: str) -> Optional[TipoListaMb]:
    """Tipo de magias do catálogo MB associado à classe conjuradora, ou None se não houver lista MB."""
    s = str(slug_classe or "").strip().lower()
    if s in ("mago", "bardo", "feiticeiro", "arcanista"):
        return "arcana"
    if s in ("clerigo", "druida", "paladino", "ranger", "cacador"):
        return "divina"
    return None


def circulo_maximo_magias_lancaveis_mb(
    slug_classe: str,
    nivel: int,
    *,
    regra_versao: Optional[str] = None,
    arcanista_caminho: Optional[str] = None,
) -> int:
    """
    Maior círculo de magia lançável (1–9) conforme nível da classe; 0 = só truques (círculo 0) ou
    nível abaixo do início de conjuração da classe.
    """
    s = str(slug_classe or "").strip().lower()
    eff = slug_efetivo_tabelas_magia_mb(s, regra_versao, arcanista_caminho)
    rv = normalizar_regra_versao(regra_versao)
    try:
        n = int(nivel)
    except (TypeError, ValueError):
        n = 1
    n = max(1, min(40, n))

    if rv == REGRA_VERSAO_V13:
        row = mapa_conjuracao_por_slug(rv).get(s)
    else:
        row = _mapa_conjuracao_por_slug().get(eff)
    if not row:
        return 0
    ini = int(row.get("conjuracao_inicia_nivel", 1) or 1)
    if n < ini:
        return 0

    # v1.3: catálogo tem apenas círculos 1–5; motor deve refletir isso na UI.
    if rv == REGRA_VERSAO_V13:
        teto_v13 = 5
        if eff in ("clerigo", "druida", "feiticeiro", "mago", "arcanista"):
            return min(teto_v13, max(1, (n + 1) // 2))
        if eff == "bardo":
            return min(teto_v13, max(1, 1 + (n - 1) // 3))
        if eff in ("paladino", "ranger", "cacador"):
            return min(teto_v13, max(1, 1 + (n - ini) // 4))
        return min(teto_v13, max(1, (n + 1) // 2))

    # MB clássico (D&D 3.5) mantém teto 9º para vínculos legados.
    if eff in ("clerigo", "druida", "feiticeiro"):
        return min(9, (n + 1) // 2)
    if eff == "mago":
        return min(9, (n + 2) // 2)
    if eff == "bardo":
        return min(6, 1 + (n - 1) // 3)
    if eff in ("paladino", "ranger"):
        return min(4, 1 + (n - ini) // 4)
    return min(9, (n + 1) // 2)
