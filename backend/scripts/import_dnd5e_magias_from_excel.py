#!/usr/bin/env python3
"""Importa magias D&D 5e da planilha PHB para o banco (uso em lote)."""

from __future__ import annotations

import argparse
import sys
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.games.dnd5e.repositories.magia_repository import Dnd5eMagiaRepository
from app.games.dnd5e.services.magia_import_service import Dnd5eMagiaImportService
from app.shared.core.database import SessionLocal


class _FakeUpload:
    def __init__(self, data: bytes):
        self._data = data

    async def read(self) -> bytes:
        return self._data


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--xlsx",
        type=Path,
        default=ROOT.parent / "data" / "dnd5e_magias_phb_p208-289.xlsx",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not args.xlsx.is_file():
        print(f"Planilha não encontrada: {args.xlsx}", file=sys.stderr)
        sys.exit(1)

    data = args.xlsx.read_bytes()
    db = SessionLocal()
    try:
        svc = Dnd5eMagiaImportService(Dnd5eMagiaRepository(db))
        import asyncio

        preview = asyncio.run(svc.preview(_FakeUpload(data)))
        print(
            f"Preview: {preview['validas']} válidas, "
            f"{len(preview.get('erros') or [])} erros"
        )
        if args.dry_run:
            return
        result = svc.confirmar(preview["import_id"])
        print(
            f"Importadas: {result['importadas']}, "
            f"atualizadas: {result['atualizadas']}, "
            f"vínculos ignorados: {result.get('vinculos_ignorados', 0)}"
        )
    finally:
        db.close()


if __name__ == "__main__":
    main()
