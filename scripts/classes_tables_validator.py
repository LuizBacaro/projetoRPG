"""
Validador do catálogo consolidado das tabelas de classes.

Validações conservadoras:
- presença das tabelas 3-3..3-18;
- quantidade mínima de linhas por tabela;
- marcadores-chave para detectar extrações quebradas.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re


@dataclass(frozen=True)
class ValidationIssue:
    level: str  # "error" | "warning"
    message: str


EXPECTED_TABLES = set(range(3, 19))

# Limiares deliberadamente baixos para não gerar falso positivo em tabela curta.
MIN_ROWS_BY_TABLE = {
    3: 20,
    4: 20,
    5: 10,
    6: 20,
    7: 10,
    8: 20,
    9: 20,
    10: 10,
    11: 20,
    12: 20,
    13: 20,
    14: 20,
    15: 5,
    16: 20,
    17: 20,
    18: 20,
}

LEVEL_TABLES = {3, 4, 6, 8, 9, 11, 12, 13, 14, 16, 17}


def _load_catalog(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Catálogo não encontrado: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_catalog(path: Path) -> list[ValidationIssue]:
    payload = _load_catalog(path)
    issues: list[ValidationIssue] = []

    tables = payload.get("tables", [])
    by_number = {t.get("table_number"): t for t in tables if isinstance(t, dict)}

    missing = sorted(EXPECTED_TABLES - set(by_number.keys()))
    if missing:
        issues.append(ValidationIssue("error", f"Tabelas ausentes no catálogo: {missing}"))

    for table_number in sorted(EXPECTED_TABLES & set(by_number.keys())):
        table = by_number[table_number]
        rows = table.get("rows", [])
        min_rows = MIN_ROWS_BY_TABLE[table_number]
        if len(rows) < min_rows:
            issues.append(
                ValidationIssue(
                    "error",
                    f"Tabela 3-{table_number} com poucas linhas ({len(rows)} < {min_rows}).",
                )
            )

        blob = _flatten_table_text(table)
        if table_number in LEVEL_TABLES:
            if not _contains_level_marker(blob, "1"):
                issues.append(
                    ValidationIssue("warning", f"Tabela 3-{table_number} sem marcador de nível 1°.")
                )
            if not _contains_level_marker(blob, "20"):
                issues.append(
                    ValidationIssue("warning", f"Tabela 3-{table_number} sem marcador de nível 20°.")
                )

        if table_number == 18:
            for term in ("Aberração", "Morto-vivo"):
                if term.lower() not in blob.lower():
                    issues.append(
                        ValidationIssue(
                            "warning", f"Tabela 3-18 sem termo esperado: {term!r}."
                        )
                    )

    return issues


def _flatten_table_text(table: dict) -> str:
    parts: list[str] = []
    for value in table.get("header", []):
        parts.append(str(value))
    for row in table.get("rows", []):
        if isinstance(row, dict):
            for value in row.values():
                parts.append(str(value))
    return " | ".join(parts)


def _contains_level_marker(blob: str, level: str) -> bool:
    # Aceita variantes com símbolo de ordinal danificado pelo OCR/layout.
    pattern = rf"(^|\D){re.escape(level)}\s*[°ºo]?($|\D)"
    return re.search(pattern, blob) is not None
