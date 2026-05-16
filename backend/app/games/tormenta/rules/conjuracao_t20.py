"""Conjuração MB — habilidade-chave, Pontos de Magia (PM) máximos por classe/nível, custo em PM por círculo."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Literal, Optional

from app.games.tormenta.rules.atributos_t20 import modificador_atributo_t20

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_CONJ_JSON = _DATA_DIR / "conjuracao_classe_mb.json"

HabilidadeChaveConjuracao = Literal["int", "sab", "car"]


@lru_cache(maxsize=1)
def _carregar_conjuracao_classe_mb() -> Dict[str, Any]:
    if not _CONJ_JSON.is_file():
        return {"classes": []}
    return json.loads(_CONJ_JSON.read_text(encoding="utf-8"))


def lista_regras_conjuracao_classe_mb() -> List[Dict[str, Any]]:
    """Linhas do JSON de conjuração (slug, chave, constantes de Pontos de Magia — PM)."""
    data = _carregar_conjuracao_classe_mb()
    rows = data.get("classes") or []
    out: List[Dict[str, Any]] = []
    if not isinstance(rows, list):
        return out
    for row in rows:
        if not isinstance(row, dict):
            continue
        slug = str(row.get("slug", "")).strip().lower()
        if not slug:
            continue
        ch = str(row.get("habilidade_chave", "")).strip().lower()
        if ch not in ("int", "sab", "car"):
            continue
        try:
            pm_c = int(row.get("pm_constante", 0))
            pm_n = int(row.get("pm_por_nivel", 0))
            ini = int(row.get("conjuracao_inicia_nivel", 1) or 1)
        except (TypeError, ValueError):
            continue
        if ini < 1 or ini > 20:
            continue
        out.append(
            {
                "slug": slug,
                "habilidade_chave": ch,
                "pm_constante": pm_c,
                "pm_por_nivel": pm_n,
                "conjuracao_inicia_nivel": ini,
            }
        )
    return sorted(out, key=lambda x: x["slug"])


def _mapa_conjuracao_por_slug() -> Dict[str, Dict[str, Any]]:
    return {str(r["slug"]).lower(): r for r in lista_regras_conjuracao_classe_mb()}


def classe_conjuracao_mb_registrada(slug: str) -> bool:
    """True se o slug está na tabela MB de conjuração (bardo, mago, paladino etc.)."""
    s = str(slug or "").strip().lower()
    return bool(s and s in _mapa_conjuracao_por_slug())


def habilidade_chave_conjuracao(
    slug_classe: str,
) -> Optional[HabilidadeChaveConjuracao]:
    """Atributo-chave de conjuração MB para o `slug` da classe, ou None se não for conjurador listado."""
    slug = str(slug_classe or "").strip().lower()
    if not slug:
        return None
    row = _mapa_conjuracao_por_slug().get(slug)
    if not row:
        return None
    ch = row.get("habilidade_chave")
    if ch in ("int", "sab", "car"):
        return ch  # type: ignore[return-value]
    return None


def _modificador_chave(
    habilidade: HabilidadeChaveConjuracao,
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
) -> int:
    if habilidade == "int":
        return modificador_atributo_t20(inteligencia)
    if habilidade == "sab":
        return modificador_atributo_t20(sabedoria)
    return modificador_atributo_t20(carisma)


def modificador_conjuracao_mb(
    slug_classe: str,
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
) -> Optional[int]:
    """Modificador da habilidade-chave de conjuração MB, ou None se a classe não conjura no catálogo."""
    hk = habilidade_chave_conjuracao(slug_classe)
    if not hk:
        return None
    return _modificador_chave(
        hk, forca, destreza, constituicao, inteligencia, sabedoria, carisma
    )


def pontos_magia_maximos_conjuracao(
    slug_classe: str,
    nivel_classe: int,
    forca: int,
    destreza: int,
    constituicao: int,
    inteligencia: int,
    sabedoria: int,
    carisma: int,
) -> Optional[int]:
    """Pontos de Magia (PM) máximos MB para a classe no nível indicado, ou None se não conjura / abaixo do nível inicial."""
    slug = str(slug_classe or "").strip().lower()
    try:
        n = int(nivel_classe)
    except (TypeError, ValueError):
        return None
    if n < 1 or n > 40:
        return None
    row = _mapa_conjuracao_por_slug().get(slug)
    if not row:
        return None
    ini = int(row["conjuracao_inicia_nivel"])
    if n < ini:
        return None
    ch: HabilidadeChaveConjuracao = row["habilidade_chave"]  # type: ignore[assignment]
    mod = _modificador_chave(
        ch, forca, destreza, constituicao, inteligencia, sabedoria, carisma
    )
    pm_c = int(row["pm_constante"])
    pm_n = int(row["pm_por_nivel"])
    if ini == 1:
        return pm_c + mod + (n - 1) * pm_n
    return pm_c + mod + (n - ini) * pm_n


# Nome legado (mana); no MB o recurso são Pontos de Magia (PM).
pontos_mana_maximos_conjuracao = pontos_magia_maximos_conjuracao


def custo_pm_preparar_ou_lancar_magia(circulo: int) -> int:
    """PM (Pontos de Magia) para preparar ou lançar: círculo 0 = 0; círculo C≥1 = C PM (MB)."""
    try:
        c = int(circulo)
    except (TypeError, ValueError):
        return 0
    if c <= 0:
        return 0
    return min(c, 20)


def texto_custo_pm_por_circulo_mb() -> str:
    data = _carregar_conjuracao_classe_mb()
    meta = data.get("_meta") if isinstance(data.get("_meta"), dict) else {}
    t = meta.get("custo_magia")
    if isinstance(t, str) and t.strip():
        return t.strip()
    return "Truque (círculo 0): 0 PM. Círculo C≥1: C PM."
