"""
Loader do catálogo canônico de habilidades especiais (D&D 3.5).

Fonte: `docs/dados/habilidades_especiais_catalogo.json`, gerado por
`processar_habilidades_especiais_excel.py` a partir da aba
`Habilidades especiais` da planilha `Características especiais_v2.xlsx`.

Localização: este módulo pertence ao pacote
`app.games.dnd35.catalogs` por ser um catálogo do PHB 3.5. Existe um
shim em `app.core.habilidades_especiais_catalog` que re-exporta os
símbolos durante a reorganização multi-jogo.

Responsabilidades (SRP):
- Resolver o caminho do artefato considerando layouts de deploy
  (Render/Vercel).
- Carregar e cachear em memória (`lru_cache`).
- Expor helpers de busca por slug, por título ou normalização textual.

Compatível com o padrão de `app.games.dnd35.catalogs.racas_catalog`
para coerência entre catálogos.
"""

from __future__ import annotations

import json
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.core.config import settings


_DEFAULT_PATH = "docs/dados/habilidades_especiais_catalogo.json"


def _sem_acentos(valor: str) -> str:
    normal = unicodedata.normalize("NFD", valor)
    return "".join(ch for ch in normal if unicodedata.category(ch) != "Mn")


def _slug(value: str) -> str:
    text = _sem_acentos(str(value or "")).lower().strip()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def _resolve_catalog_path() -> Path:
    path = Path(_DEFAULT_PATH)
    candidate_backend = settings.BASE_DIR / path
    if candidate_backend.is_file():
        return candidate_backend
    return settings.BASE_DIR.parent / path


@lru_cache(maxsize=1)
def load_catalog() -> dict[str, Any]:
    path = _resolve_catalog_path()
    if not path.is_file():
        return {"habilidades": []}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {"habilidades": []}


def list_habilidades() -> list[dict[str, Any]]:
    payload = load_catalog()
    data = payload.get("habilidades", [])
    return data if isinstance(data, list) else []


def get_habilidade_by_slug(value: str | None) -> dict[str, Any] | None:
    key = _slug(value or "")
    if not key:
        return None
    for item in list_habilidades():
        if not isinstance(item, dict):
            continue
        if _slug(item.get("slug", "")) == key:
            return item
        if _slug(item.get("titulo", "")) == key:
            return item
        for alias in item.get("aliases", []) or []:
            if _slug(str(alias)) == key:
                return item
    return None


def resolver_por_texto(texto: str | None) -> dict[str, Any] | None:
    """
    Busca habilidade canônica por texto livre (ex.: item extraído da coluna
    'Especial' de uma tabela de classe). Normaliza pontuação e casamento
    parcial (prefixo) para casos comuns como "Fúria (1/dia)" → "Fúria".
    """
    if not texto:
        return None
    alvo = _slug(texto)
    if not alvo:
        return None
    # 1) match direto por slug/título
    direto = get_habilidade_by_slug(alvo)
    if direto:
        return direto

    # 2) match por prefixo progressivo (remove trechos entre parênteses e
    #    sufixos comuns como "1/dia", "+X").
    limpo = re.sub(r"\([^)]*\)", " ", texto)
    limpo = re.sub(r"[+\-]?\d+/[\wº]+", " ", limpo)
    limpo = re.sub(r"[+\-]\d+", " ", limpo)
    limpo = re.sub(r"\s+", " ", limpo).strip()
    if limpo and limpo != texto:
        tentativa = get_habilidade_by_slug(limpo)
        if tentativa:
            return tentativa

    # 3) match por prefixo (greedy) contra catálogo
    candidatos = list_habilidades()
    melhor: dict[str, Any] | None = None
    melhor_len = 0
    for item in candidatos:
        titulo_slug = _slug(item.get("titulo", ""))
        if not titulo_slug:
            continue
        if alvo.startswith(titulo_slug) and len(titulo_slug) > melhor_len:
            melhor = item
            melhor_len = len(titulo_slug)
    return melhor


__all__ = [
    "get_habilidade_by_slug",
    "list_habilidades",
    "load_catalog",
    "resolver_por_texto",
]
