"""Grimório MB — validação de papéis (preparar vs espontâneo) e gasto de PM."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Tuple

from app.games.tormenta.rules.catalogo_t20 import metadados_magia_mb_por_slug
from app.games.tormenta.rules.conjuracao_t20 import (
    custo_pm_preparar_ou_lancar_magia,
    pontos_magia_maximos_conjuracao,
)

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CONJ_JSON = _DATA_DIR / "conjuracao_classe_mb.json"

ModoConjuracaoMb = Literal["preparar", "espontaneo"]
_PAPEIS = frozenset({"grimorio", "conhecida", "preparada"})


@lru_cache(maxsize=1)
def _carregar_conj() -> Dict[str, Any]:
    if not _CONJ_JSON.is_file():
        return {"classes": []}
    return json.loads(_CONJ_JSON.read_text(encoding="utf-8"))


def modo_conjuracao_classe_mb(slug_classe: str) -> Optional[ModoConjuracaoMb]:
    """preparar (mago/clérigo/druida/paladino/ranger) ou espontaneo (bardo/feiticeiro)."""
    s = str(slug_classe or "").strip().lower()
    rows = _carregar_conj().get("classes") or []
    if not isinstance(rows, list):
        return None
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("slug", "")).strip().lower() != s:
            continue
        modo = str(row.get("modo_conjuracao", "preparar") or "preparar").strip().lower()
        if modo in ("preparar", "espontaneo"):
            return modo  # type: ignore[return-value]
        return "preparar"
    return None


def _classe_usa_livro_grimorio_mb(slug_classe: str) -> bool:
    from app.games.tormenta.rules.magias_grimorio_aprendizado_t20 import (
        classe_usa_limite_grimorio_mb,
    )

    return classe_usa_limite_grimorio_mb(slug_classe)


def _classe_usa_repertorio_aprendido_mb(slug_classe: str) -> bool:
    from app.games.tormenta.rules.magias_repertorio_aprendido_t20 import (
        classe_usa_limite_repertorio_mb,
    )

    return classe_usa_limite_repertorio_mb(slug_classe)


def validar_papel_magia_para_classe(
    slug_classe: str,
    papel: str,
    *,
    conjuracao_manual: bool = False,
) -> Tuple[bool, str]:
    """Valida se o papel (grimorio/conhecida/preparada) é permitido para a classe MB."""
    if conjuracao_manual:
        return True, ""
    p = str(papel or "").strip().lower()
    if p not in _PAPEIS:
        return False, "papel deve ser grimorio, conhecida ou preparada"
    modo = modo_conjuracao_classe_mb(slug_classe)
    if modo is None:
        return True, ""
    if modo == "espontaneo":
        if p == "grimorio":
            return (
                False,
                "Classes espontâneas (bardo, feiticeiro) não usam grimório no MB — use conhecida.",
            )
        return True, ""
    # preparar
    if p == "conhecida":
        if _classe_usa_repertorio_aprendido_mb(slug_classe):
            return True, ""
        return (
            False,
            "O mago usa grimório (livro) — papel conhecida não se aplica; use grimorio.",
        )
    if p == "grimorio" and not _classe_usa_livro_grimorio_mb(slug_classe):
        return (
            False,
            "Clérigo, druida, paladino e ranger não usam livro de magias (MB) — use repertório aprendido (conhecida).",
        )
    return True, ""


def custo_pm_magia_slug(magia_slug: str) -> int:
    meta = metadados_magia_mb_por_slug(magia_slug)
    if not meta:
        return 0
    try:
        circulo = int(meta.get("circulo", 0) or 0)
    except (TypeError, ValueError):
        circulo = 0
    return custo_pm_preparar_ou_lancar_magia(circulo)


def simular_gasto_pm(
    *,
    classe_slug: str,
    nivel: int,
    for_valor: int,
    des_valor: int,
    con_valor: int,
    int_valor: int,
    sab_valor: int,
    car_valor: int,
    pa_atual: int,
    magia_slug: str,
    custo_pm_override: Optional[int] = None,
) -> Dict[str, Any]:
    """Calcula custo e novo saldo de PM sem persistir."""
    if custo_pm_override is not None:
        custo = int(custo_pm_override)
    else:
        custo = custo_pm_magia_slug(magia_slug)
    pm_max = pontos_magia_maximos_conjuracao(
        classe_slug,
        nivel,
        for_valor,
        des_valor,
        con_valor,
        int_valor,
        sab_valor,
        car_valor,
    )
    atual = int(pa_atual)
    novo = atual - custo
    permitido = novo >= 0 or custo == 0
    return {
        "custo_pm": custo,
        "pa_atual_antes": atual,
        "pa_atual_depois": novo,
        "pa_max": pm_max,
        "permitido": permitido,
        "motivo": "" if permitido else "PM insuficientes para lançar esta magia.",
    }
