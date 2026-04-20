"""
Catálogo de tabelas de classes (experimental e opt-in).

Este módulo não altera comportamento funcional de APIs existentes.
Ele apenas carrega e valida minimamente o JSON consolidado quando habilitado
por feature flag.
"""

from __future__ import annotations

from pathlib import Path
import json
import logging

from .config import settings

logger = logging.getLogger(__name__)


def _resolve_catalog_path() -> Path:
    raw = settings.CLASSES_TABLES_CATALOG_PATH
    path = Path(raw)
    if path.is_absolute():
        return path
    candidate_backend = settings.BASE_DIR / raw
    if candidate_backend.is_file():
        return candidate_backend
    return settings.BASE_DIR.parent / raw


def load_classes_tables_catalog() -> dict:
    path = _resolve_catalog_path()
    if not path.is_file():
        raise FileNotFoundError(f"Catálogo de classes não encontrado: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    if "tables" not in payload or not isinstance(payload["tables"], list):
        raise ValueError("Catálogo de classes inválido: campo 'tables' ausente.")
    return payload


def initialize_classes_tables_catalog() -> None:
    """
    Inicializa o catálogo em modo seguro (somente leitura).

    - Por padrão, não executa nada (feature flag desligada).
    - Quando ligado, valida presença do arquivo e estrutura mínima.
    """
    if not settings.CLASSES_TABLES_CATALOG_ENABLED:
        logger.info("ℹ️  Catálogo de classes desabilitado por feature flag.")
        return

    payload = load_classes_tables_catalog()
    logger.info(
        "✅ Catálogo de classes carregado: %s tabela(s).",
        len(payload.get("tables", [])),
    )
