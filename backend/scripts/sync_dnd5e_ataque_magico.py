#!/usr/bin/env python3
"""Preenche dnd5e_magias.ataque_magico a partir do JSON SRD."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.games.dnd5e.models.magia import Dnd5eMagia
from app.repositories.base import commit_with_rollback
from app.shared.core.database import SessionLocal

SRD = Path(__file__).resolve().parents[1] / "data" / "dnd5e_srd_spells_en.json"


def main() -> None:
    spells = json.loads(SRD.read_text(encoding="utf-8"))
    by_slug = {s["index"]: s.get("attack_type") for s in spells}
    db = SessionLocal()
    n = 0
    try:
        for row in db.query(Dnd5eMagia):
            atk = by_slug.get(row.slug)
            val = atk if atk in ("ranged", "melee") else None
            if row.ataque_magico != val:
                row.ataque_magico = val
                n += 1
        commit_with_rollback(db)
        print(f"ataque_magico atualizado em {n} magias.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
