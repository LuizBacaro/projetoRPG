"""Idiomas D&D 5E — catálogo e validação na ficha."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence

from app.games.dnd5e.data.antecedentes_catalogo import ANTECEDENTES_CATALOGO
from app.games.dnd5e.data.idiomas_catalogo import (
    IDIOMAS_CATALOGO,
    IDIOMAS_SLUGS_VALIDOS,
)

_PLACEHOLDER_RE = re.compile(r"^idioma_extra_\d+$", re.IGNORECASE)


def lista_idiomas_catalogo() -> List[Dict[str, Any]]:
    return [dict(row) for row in IDIOMAS_CATALOGO]


def idioma_por_slug(slug: str) -> Optional[Dict[str, Any]]:
    key = (slug or "").strip().lower()
    for row in IDIOMAS_CATALOGO:
        if row["slug"] == key:
            return dict(row)
    return None


def normalizar_idiomas_escolhidos(raw: Any) -> List[str]:
    if not isinstance(raw, (list, tuple)):
        return []
    out: List[str] = []
    seen: set[str] = set()
    for item in raw:
        slug = str(item or "").strip().lower()
        if not slug or _PLACEHOLDER_RE.match(slug):
            continue
        if slug not in IDIOMAS_SLUGS_VALIDOS or slug in seen:
            continue
        out.append(slug)
        seen.add(slug)
    return out


def validar_idiomas_antecedente(
    idiomas: Sequence[str],
    *,
    qtd_esperada: int,
) -> List[str]:
    qtd = max(0, int(qtd_esperada))
    escolhidos = normalizar_idiomas_escolhidos(idiomas)
    if qtd == 0:
        if escolhidos:
            raise ValueError("Este antecedente não concede idiomas extras")
        return []
    if len(escolhidos) != qtd:
        raise ValueError(
            f"Escolha exatamente {qtd} idioma(s) do antecedente "
            f"({len(escolhidos)} selecionado(s))"
        )
    return escolhidos


def _idiomas_qtd_antecedente(slug: str) -> int:
    key = (slug or "").strip().lower()
    for row in ANTECEDENTES_CATALOGO:
        if row.get("slug") == key:
            return int(row.get("idiomas_qtd", 0))
    return 0


def validar_idiomas_antecedente_na_ficha(ficha: Dict[str, Any]) -> List[str]:
    slug = (ficha.get("antecedente_slug") or "").strip().lower() or None
    if not slug:
        raw = ficha.get("antecedente_idiomas") or []
        if normalizar_idiomas_escolhidos(raw):
            raise ValueError("Idiomas de antecedente exigem um antecedente selecionado")
        return []

    qtd = _idiomas_qtd_antecedente(slug)
    if qtd <= 0 and slug not in {r.get("slug") for r in ANTECEDENTES_CATALOGO}:
        return normalizar_idiomas_escolhidos(ficha.get("antecedente_idiomas") or [])

    return validar_idiomas_antecedente(
        ficha.get("antecedente_idiomas") or [],
        qtd_esperada=qtd,
    )
