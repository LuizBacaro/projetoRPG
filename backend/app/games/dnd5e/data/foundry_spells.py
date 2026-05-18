"""Parsing de magias do compêndio Foundry dnd5e-pt-br."""

from __future__ import annotations

import re
import unicodedata
from html import unescape

_MARCADORES_NIVEL_SUPERIOR = (
    "Em Círculos Superiores",
    "Em Níveis Superiores",
    "At Higher Levels",
)


def slugify_en(name: str) -> str:
    base = (
        unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    )
    return re.sub(r"[^a-z0-9]+", "-", base).strip("-")


def html_para_texto(html: str) -> str:
    if not html or not str(html).strip():
        return ""
    t = str(html)
    t = re.sub(r"<br\s*/?>", "\n", t, flags=re.I)
    t = re.sub(r"</p>\s*", "\n\n", t, flags=re.I)
    t = re.sub(r"<p[^>]*>", "", t, flags=re.I)
    t = re.sub(r"<strong>", "**", t, flags=re.I)
    t = re.sub(r"</strong>", "**", t, flags=re.I)
    t = re.sub(r"<[^>]+>", "", t)
    t = unescape(t)
    t = re.sub(r"[ \t]+\n", "\n", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def separar_descricao_foundry(html: str) -> tuple[str, str | None]:
    """Texto principal + bloco de níveis superiores (PHB PT Foundry)."""
    texto = html_para_texto(html)
    if not texto:
        return "", None

    idx_split: int | None = None
    for marcador in _MARCADORES_NIVEL_SUPERIOR:
        pos = texto.find(marcador)
        if pos >= 0 and (idx_split is None or pos < idx_split):
            idx_split = pos

    if idx_split is None:
        return texto, None

    principal = texto[:idx_split].strip()
    superior = texto[idx_split:].strip()
    return principal, superior or None


def extrair_traducao_entry(key: str, entry: dict) -> dict[str, str]:
    slug = slugify_en(key)
    nome_pt = (entry.get("name") or "").strip()
    html = entry.get("description") or ""
    principal, superior = separar_descricao_foundry(html)
    data: dict[str, str] = {
        "nome": nome_pt,
        "nome_en": key.strip(),
    }
    if principal:
        data["descricao"] = principal
    if superior:
        data["descricao_nivel_superior"] = superior
    return slug, data
