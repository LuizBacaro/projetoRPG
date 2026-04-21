"""
Runner unificado dos catálogos gerados a partir das planilhas Excel.

Hoje executa, em sequência e de forma independente:
1. Catálogo de raças (`Características especiais.xlsx` ou v2).
2. Catálogo de habilidades especiais (`Características especiais_v2.xlsx`).

Uso:
    python -m scripts.run_catalogs
    python -m scripts.run_catalogs --racas-source "Características especiais_v2.xlsx"
    python -m scripts.run_catalogs --dry-run

Exit code:
    0 se todos os catálogos foram gerados sem erros de validação;
    1 se pelo menos um pipeline falhou ou emitiu erro de validação.

Observação:
    Este runner é um agregador — cada pipeline continua respondendo aos
    seus próprios entrypoints (`processar_*_excel.py`) para compatibilidade.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

# Garante que `scripts/` esteja no sys.path mesmo quando executado como
# módulo pelo interpretador (ex.: `python -m scripts.run_catalogs`).
_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from habilidades_especiais_catalog_pipeline import (  # noqa: E402
    HabilidadesCatalogExporter,
    HabilidadesCatalogPipeline,
    HabilidadesNormalizer,
    HabilidadesWorkbookReader,
)
from racas_catalog_pipeline import (  # noqa: E402
    RacasCatalogExporter,
    RacasCatalogPipeline,
    RacasNormalizer,
    RacasWorkbookReader,
)
from racas_catalog_validator import validate_records  # noqa: E402


DEFAULT_RACAS_SOURCE = Path("Características especiais.xlsx")
DEFAULT_RACAS_OUTPUT = Path("docs/dados/racas_caracteristicas_catalogo.json")
DEFAULT_HABILIDADES_SOURCE = Path("Características especiais_v2.xlsx")
DEFAULT_HABILIDADES_OUTPUT = Path(
    "docs/dados/habilidades_especiais_catalogo.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Executa todos os pipelines de catálogo derivados das planilhas "
            "do projeto Arena TTRPG."
        )
    )
    parser.add_argument("--racas-source", type=Path, default=DEFAULT_RACAS_SOURCE)
    parser.add_argument("--racas-output", type=Path, default=DEFAULT_RACAS_OUTPUT)
    parser.add_argument(
        "--habilidades-source", type=Path, default=DEFAULT_HABILIDADES_SOURCE
    )
    parser.add_argument(
        "--habilidades-output", type=Path, default=DEFAULT_HABILIDADES_OUTPUT
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Falha se qualquer pipeline emitir warning ou erro de validação.",
    )
    return parser.parse_args()


def _executar_racas(args: argparse.Namespace) -> tuple[int, int]:
    exporter = None if args.dry_run else RacasCatalogExporter(args.racas_output)
    pipeline = RacasCatalogPipeline(
        reader=RacasWorkbookReader(args.racas_source),
        normalizer=RacasNormalizer(),
        exporter=exporter,
    )
    resultado = pipeline.run()
    issues = validate_records(resultado.racas)
    erros = [i for i in issues if i.level == "error"]
    warnings = [i for i in issues if i.level == "warning"]
    print(
        f"[raças] {len(resultado.racas)} raça(s) • "
        f"{len(resultado.warnings)} warning(s) de parser • "
        f"{len(erros)} erro(s) de validação • "
        f"{len(warnings)} warning(s) de validação"
    )
    return len(erros), len(resultado.warnings) + len(warnings)


def _executar_habilidades(args: argparse.Namespace) -> tuple[int, int]:
    exporter = (
        None
        if args.dry_run
        else HabilidadesCatalogExporter(args.habilidades_output)
    )
    pipeline = HabilidadesCatalogPipeline(
        reader=HabilidadesWorkbookReader(args.habilidades_source),
        normalizer=HabilidadesNormalizer(),
        exporter=exporter,
    )
    resultado = pipeline.run()
    print(
        f"[habilidades] {len(resultado.habilidades)} habilidade(s) • "
        f"{len(resultado.warnings)} warning(s) de parser"
    )
    return 0, len(resultado.warnings)


def main() -> int:
    args = _parse_args()

    total_erros = 0
    total_warnings = 0
    for step_label, step in (
        ("raças", _executar_racas),
        ("habilidades especiais", _executar_habilidades),
    ):
        try:
            erros, warnings_qt = step(args)
        except Exception as exc:  # noqa: BLE001
            print(f"❌ Falha no pipeline de {step_label}: {exc}")
            return 1
        total_erros += erros
        total_warnings += warnings_qt

    if total_erros > 0:
        print("❌ Geração concluída com erros de validação.")
        return 1
    if args.strict and total_warnings > 0:
        print("❌ Modo --strict: warnings tratados como erro.")
        return 1
    print(
        "✅ Todos os catálogos foram gerados com sucesso "
        f"({total_warnings} warning(s) tolerado(s))."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
