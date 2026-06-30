"""Poderes automáticos v1.3 — origem, concedido e humano Versátil."""

from __future__ import annotations

import re
import unicodedata
from typing import Any, Dict, List, Optional

from app.games.tormenta.rules.catalogo_t20 import lista_talentos_mb_catalogo
from app.games.tormenta.rules.regra_versao_t20 import (
    REGRA_VERSAO_V13,
    regra_versao_de_ficha,
)

AUTO_PODER_NOTA_PREFIX = "auto:v13:"


def _normalizar_slug(texto: str) -> str:
    s = unicodedata.normalize("NFKD", str(texto or ""))
    s = s.encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def nome_poder_por_slug_v13(slug: str) -> str:
    """Resolve slug v1.3 para nome exibido (catálogo MB ou título a partir do slug)."""
    s = _normalizar_slug(slug)
    if not s:
        return ""
    for row in lista_talentos_mb_catalogo():
        nome = str(row.get("nome", "")).strip()
        if nome and _normalizar_slug(nome) == s:
            return nome
    return s.replace("_", " ").title()


def slugs_poderes_de_beneficios_origem(beneficios: Any) -> List[str]:
    out: List[str] = []
    if not isinstance(beneficios, list):
        return out
    seen: set[str] = set()
    for raw in beneficios:
        key = str(raw or "").strip().lower()
        if not key.startswith("poder:"):
            continue
        slug = _normalizar_slug(key.split(":", 1)[1])
        if slug and slug not in seen:
            seen.add(slug)
            out.append(slug)
    return out


def nota_auto_poder_v13(tipo: str, slug: str) -> str:
    return f"{AUTO_PODER_NOTA_PREFIX}{tipo}:{_normalizar_slug(slug)}"


def listar_poderes_sync_v13(ficha_json: Optional[dict]) -> List[Dict[str, str]]:
    """
    Poderes que a ficha v1.3 deve ter em SQL (somente fontes automáticas).
    Retorna dicts com slug, nome, notas.
    """
    fj = dict(ficha_json or {})
    if regra_versao_de_ficha(fj) != REGRA_VERSAO_V13:
        return []

    out: List[Dict[str, str]] = []
    seen_notas: set[str] = set()

    def _add(tipo: str, slug: str) -> None:
        s = _normalizar_slug(slug)
        if not s:
            return
        nota = nota_auto_poder_v13(tipo, s)
        if nota in seen_notas:
            return
        seen_notas.add(nota)
        out.append(
            {
                "slug": s,
                "nome": nome_poder_por_slug_v13(s),
                "notas": nota,
            }
        )

    for slug in slugs_poderes_de_beneficios_origem(fj.get("origem_beneficios")):
        _add("origem", slug)

    pcs = str(fj.get("poder_concedido_slug") or "").strip()
    if pcs:
        _add("concedido", pcs)

    versatil = str(fj.get("humano_versatil") or "").strip().lower()
    if versatil == "pericia_poder":
        hvs = str(fj.get("humano_versatil_poder_slug") or "").strip()
        if hvs:
            _add("versatil", hvs)

    return out
