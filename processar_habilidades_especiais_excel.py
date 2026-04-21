"""
Gera o catálogo canônico de habilidades especiais a partir da aba
`Habilidades especiais` da planilha `Características especiais_v2.xlsx`.

Uso:
    python processar_habilidades_especiais_excel.py
    python processar_habilidades_especiais_excel.py --source "Características especiais_v2.xlsx"
    python processar_habilidades_especiais_excel.py --source <planilha> --output <json>

Flags:
    --dry-run    não escreve o arquivo de saída
    --strict     falha com código 1 se houver qualquer warning
"""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.habilidades_especiais_catalog_pipeline import (
    HabilidadesCatalogExporter,
    HabilidadesCatalogPipeline,
    HabilidadesNormalizer,
    HabilidadesWorkbookReader,
    ParseResult,
)


DEFAULT_SOURCE = Path("Características especiais_v2.xlsx")
DEFAULT_OUTPUT = Path("docs/dados/habilidades_especiais_catalogo.json")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Processa a aba 'Habilidades especiais' da planilha v2 e gera o "
            "catálogo canônico em JSON."
        )
    )
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--strict", action="store_true")
    return parser.parse_args()


def _relatar_warnings(resultado: ParseResult) -> int:
    if not resultado.warnings:
        print("ℹ️  Parser executado sem warnings.")
        return 0
    print(f"⚠️  {len(resultado.warnings)} warning(s) durante o parsing:")
    for warn in resultado.warnings:
        print(f"   - [{warn.titulo}] {warn.campo}: {warn.mensagem}")
    return len(resultado.warnings)


def main() -> int:
    args = _parse_args()

    exporter = None if args.dry_run else HabilidadesCatalogExporter(args.output)
    pipeline = HabilidadesCatalogPipeline(
        reader=HabilidadesWorkbookReader(args.source),
        normalizer=HabilidadesNormalizer(),
        exporter=exporter,
    )
    resultado = pipeline.run()
    qt_warn = _relatar_warnings(resultado)

    if args.dry_run:
        print(
            f"🔎 Dry-run concluído ({len(resultado.habilidades)} habilidade(s) "
            f"lidas de {args.source})."
        )
    else:
        print(
            f"✅ Catálogo de habilidades especiais gerado: {args.output} "
            f"({len(resultado.habilidades)} habilidade(s))"
        )

    if args.strict and qt_warn > 0:
        print("❌ Modo --strict: warnings tratados como erro.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
