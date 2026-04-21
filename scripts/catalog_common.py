"""
Utilidades comuns aos pipelines de catálogos gerados a partir de planilhas
Excel (raças, habilidades especiais, etc.).

Objetivo:
- Consolidar helpers duplicados (normalização textual, slug, split por
  múltiplos delimitadores) em um único lugar, reduzindo divergência técnica
  entre os pipelines `scripts/racas_catalog_pipeline.py` e
  `scripts/habilidades_especiais_catalog_pipeline.py`.
- Padronizar o envelope do JSON exportado (`source`, `generated_at`,
  `total_*`, `items`) para facilitar leitura/diagnóstico dos artefatos em
  `docs/dados/`.

Escopo:
- Apenas utilidades puras e sem estado. Não toca em I/O de workbook para
  manter cada pipeline responsável pelo seu próprio leitor (SRP).
"""

from __future__ import annotations

from datetime import datetime, timezone
import re
import unicodedata
from typing import Any, Iterable


def sem_acentos(valor: str) -> str:
    """Remove diacríticos preservando letras/dígitos."""
    normal = unicodedata.normalize("NFD", valor)
    return "".join(ch for ch in normal if unicodedata.category(ch) != "Mn")


def slug(valor: str) -> str:
    """Gera slug estável (minúsculo, hífen, sem acentos)."""
    base = sem_acentos(str(valor or "")).lower().strip()
    base = re.sub(r"[^a-z0-9]+", "-", base)
    return base.strip("-")


def texto_limpo(valor: Any) -> str:
    """Converte para string, remove espaços e descarta placeholders nulos."""
    if valor is None:
        return ""
    texto = str(valor).strip()
    if texto.lower() in {"nan", "none"}:
        return ""
    return texto


def split_tokens(texto: Any, *, delimitadores: str = ";,\n") -> list[str]:
    """
    Divide texto em tokens aceitando múltiplos delimitadores.

    Por padrão aceita `;`, `,` e quebra de linha, cobrindo variações
    observadas entre `Características especiais.xlsx` e
    `Características especiais_v2.xlsx`.
    """
    limpo = texto_limpo(texto)
    if not limpo:
        return []
    padrao = "[" + re.escape(delimitadores) + "]"
    return [tok.strip() for tok in re.split(padrao, limpo) if tok.strip()]


def build_envelope(
    source_path: str | None,
    items_key: str,
    items: list[dict[str, Any]],
    *,
    extras: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Produz o envelope padrão dos JSONs exportados pelos pipelines.

    Args:
        source_path: caminho (absoluto ou relativo) da planilha original.
        items_key: chave do payload onde o array será publicado
            (ex.: ``"racas"`` ou ``"habilidades"``).
        items: lista de registros já normalizados.
        extras: dicionário opcional com campos adicionais a serem mesclados.
    """
    total_key = f"total_{items_key}"
    payload: dict[str, Any] = {
        "source": source_path or "",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        total_key: len(items),
        items_key: items,
    }
    if extras:
        for key, value in extras.items():
            if key in payload:
                continue
            payload[key] = value
    return payload


def iter_listas_limpas(valores: Iterable[Any]) -> list[str]:
    """Converte iterável em lista de strings não vazias, trimadas."""
    return [str(v).strip() for v in valores if str(v).strip()]


__all__ = [
    "build_envelope",
    "iter_listas_limpas",
    "sem_acentos",
    "slug",
    "split_tokens",
    "texto_limpo",
]
