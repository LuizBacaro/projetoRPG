"""Restaura snapshot completo dos personagens e seus relacionamentos."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.personagens_snapshot_utils import restore_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Restaura um snapshot JSON de personagens no banco configurado em DATABASE_URL."
    )
    parser.add_argument("--input", required=True, type=Path, help="Arquivo JSON do snapshot.")
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Sobrescreve personagens ja existentes com mesma chave natural (nome, tipo, classe, dono_id).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    resultado = restore_snapshot(args.input, replace_existing=args.replace_existing)

    print(f"Snapshot processado: {resultado['total_snapshot']}")
    print(f"Combatentes criados: {resultado['criados']}")
    print(f"Combatentes atualizados: {resultado['atualizados']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())