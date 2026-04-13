"""Exporta snapshot completo dos personagens e seus relacionamentos."""

from __future__ import annotations

import argparse
from pathlib import Path

from scripts.personagens_snapshot_utils import build_snapshot, default_snapshot_path, write_snapshot


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exporta um snapshot JSON dos personagens salvos no banco configurado em DATABASE_URL."
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Caminho do arquivo JSON de saida. Se omitido, grava em backend/scripts/generated/.",
    )
    parser.add_argument(
        "--include-deleted",
        action="store_true",
        help="Inclui personagens com soft delete no snapshot.",
    )
    parser.add_argument(
        "--tipo",
        action="append",
        dest="tipos",
        help="Filtra por tipo de combatente. Pode repetir: --tipo jogador --tipo npc",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_path = args.output or default_snapshot_path()

    snapshot = build_snapshot(include_deleted=args.include_deleted, tipos=args.tipos)
    write_snapshot(snapshot, output_path)

    print(f"Snapshot salvo em: {output_path}")
    print(f"Combatentes exportados: {snapshot['total_combatentes']}")
    if snapshot["tipos"]:
        print(f"Tipos filtrados: {', '.join(snapshot['tipos'])}")
    if snapshot["include_deleted"]:
        print("Soft delete incluido: sim")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())