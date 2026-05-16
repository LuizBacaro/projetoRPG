"""
Consolida as planilhas de classes (Tabela 3-3 até 3-18) em um catálogo JSON.

Fluxo seguro:
- Não altera backend, frontend, banco ou seeds existentes.
- Apenas lê `tabelas_classes_excel/*.xlsx`.
- Gera artefato em `docs/dados/tabelas_classes_catalogo.json`.
"""

from __future__ import annotations

from pathlib import Path

from scripts.classes_tables_pipeline import (
    ClassTableCatalogExporter,
    ClassTableNormalizer,
    ClassTablePipeline,
    ClassTableWorkbookReader,
)
from scripts.classes_tables_validator import validate_catalog


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "tabelas_classes_excel"
OUTPUT_JSON = BASE_DIR / "docs" / "dados" / "tabelas_classes_catalogo.json"


def main() -> int:
    pipeline = ClassTablePipeline(
        reader=ClassTableWorkbookReader(INPUT_DIR),
        normalizer=ClassTableNormalizer(),
        exporter=ClassTableCatalogExporter(OUTPUT_JSON),
    )
    output_path = pipeline.run()
    issues = validate_catalog(output_path)
    errors = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    for issue in warnings:
        print(f"⚠️  {issue.message}")
    if errors:
        for issue in errors:
            print(f"❌ {issue.message}")
        raise SystemExit(1)
    print(f"✅ Catálogo gerado: {output_path}")
    if warnings:
        print(f"ℹ️  Validação concluída com {len(warnings)} aviso(s).")
    else:
        print("✅ Validação concluída sem avisos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
