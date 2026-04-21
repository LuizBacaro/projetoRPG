"""
Gera o catálogo racial normalizado a partir da planilha
`Características especiais.xlsx` (ou `Características especiais_v2.xlsx`).

Uso:
    python processar_caracteristicas_especiais_excel.py
    python processar_caracteristicas_especiais_excel.py --source "Características especiais_v2.xlsx"
    python processar_caracteristicas_especiais_excel.py --source <planilha> --output <json>

A lógica de parsing está em `scripts/racas_catalog_pipeline.py` e a validação
em `scripts/racas_catalog_validator.py`. Este arquivo é apenas o ponto de
entrada operacional.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.racas_catalog_pipeline import (
    ParseResult,
    RacasCatalogExporter,
    RacasCatalogPipeline,
    RacasNormalizer,
    RacasWorkbookReader,
)
from scripts.racas_catalog_validator import validate_records


DEFAULT_SOURCE = Path("Características especiais.xlsx")
DEFAULT_OUTPUT = Path("docs/dados/racas_caracteristicas_catalogo.json")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Processa a planilha de características raciais e gera o catálogo "
            "canônico em JSON."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=DEFAULT_SOURCE,
        help="Caminho da planilha de origem (.xlsx).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Caminho do JSON de saída.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Falha com código 1 se houver qualquer warning ou erro de validação.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Processa a planilha sem escrever o JSON (útil para checagem).",
    )
    return parser.parse_args()


def _relatar_warnings(resultado: ParseResult) -> int:
    if not resultado.warnings:
        print("ℹ️  Parser executado sem warnings.")
        return 0
    print(f"⚠️  {len(resultado.warnings)} warning(s) durante o parsing:")
    for warn in resultado.warnings:
        alvo = warn.raca or "(geral)"
        detalhe = f" [{warn.token!r}]" if warn.token else ""
        print(f"   - [{alvo}] {warn.campo}: {warn.mensagem}{detalhe}")
    return len(resultado.warnings)


def _relatar_validacao(resultado: ParseResult) -> tuple[int, int]:
    issues = validate_records(resultado.racas)
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    for issue in warnings:
        print(f"⚠️  {issue.message}")
    for issue in errors:
        print(f"❌ {issue.message}")
    return len(errors), len(warnings)


def main() -> int:
    args = _parse_args()

    exporter = None if args.dry_run else RacasCatalogExporter(args.output)
    pipeline = RacasCatalogPipeline(
        reader=RacasWorkbookReader(args.source),
        normalizer=RacasNormalizer(),
        exporter=exporter,
    )
    resultado = pipeline.run()

    qt_warn_parser = _relatar_warnings(resultado)
    qt_err_val, qt_warn_val = _relatar_validacao(resultado)

    if args.dry_run:
        print(
            f"🔎 Dry-run concluído ({len(resultado.racas)} raça(s) lidas de "
            f"{args.source})."
        )
    else:
        print(
            f"✅ Catálogo racial gerado: {args.output} "
            f"({len(resultado.racas)} raça(s))"
        )

    if qt_err_val > 0:
        return 1
    if args.strict and (qt_warn_parser > 0 or qt_warn_val > 0):
        print("❌ Modo --strict: warnings tratados como erro.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
