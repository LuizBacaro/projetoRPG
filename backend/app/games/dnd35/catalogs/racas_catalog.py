"""
Loader do catálogo canônico de raças (D&D 3.5).

Fonte: `docs/dados/racas_caracteristicas_catalogo.json`, gerado pelo
pipeline de planilhas do projeto.

Localização: `app.games.dnd35.catalogs`.
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.shared.core.config import settings

_DEFAULT_PATH = "docs/dados/racas_caracteristicas_catalogo.json"


def _slug(value: str) -> str:
    text = unicodedata.normalize("NFD", str(value or ""))
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _resolve_catalog_path() -> Path:
    path = Path(_DEFAULT_PATH)
    candidate_backend = settings.BASE_DIR / path
    if candidate_backend.is_file():
        return candidate_backend
    return settings.BASE_DIR.parent / path


@lru_cache(maxsize=1)
def load_racas_catalog() -> dict[str, Any]:
    path = _resolve_catalog_path()
    if not path.is_file():
        return {"racas": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"racas": []}


def list_racas() -> list[dict[str, Any]]:
    payload = load_racas_catalog()
    racas = payload.get("racas", [])
    return racas if isinstance(racas, list) else []


def get_raca_by_slug_or_name(value: str | None) -> dict[str, Any] | None:
    key = _slug(value or "")
    if not key:
        return None
    for raca in list_racas():
        if not isinstance(raca, dict):
            continue
        slug_key = _slug(raca.get("slug", ""))
        nome_key = _slug(raca.get("nome", ""))
        variants = {slug_key, nome_key}
        if slug_key.endswith("s"):
            variants.add(slug_key[:-1])
        if nome_key.endswith("s"):
            variants.add(nome_key[:-1])
        if key in variants:
            return raca
    return None


__all__ = [
    "load_racas_catalog",
    "list_racas",
    "get_raca_by_slug_or_name",
]
