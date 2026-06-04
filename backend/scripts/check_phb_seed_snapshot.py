#!/usr/bin/env python3
"""
Compara totais de magias no seed (sem PDF) com o snapshot em docs/diff-phb-seed-all-classes.json.

Uso (CI ou local):
  cd backend && python3 scripts/check_phb_seed_snapshot.py

Atualizar snapshot após mudança intencional no seed + diff PHB com PDF local:
  python3 scripts/diff_phb_seed_all_classes.py --json ../docs/diff-phb-seed-all-classes.json
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
SNAPSHOT = REPO / "docs" / "diff-phb-seed-all-classes.json"

# Reutiliza parser do diff PHB
sys.path.insert(0, str(ROOT / "scripts"))
from diff_phb_seed_all_classes import CLASSES, load_seed_class  # noqa: E402


def seed_total_unique(cfg: dict) -> int:
    seed, _, _dupes = load_seed_class(cfg)
    return sum(len(set(seed.get(i, []))) for i in range(10))


def main() -> int:
    if not SNAPSHOT.is_file():
        print(f"::error::Snapshot ausente: {SNAPSHOT}")
        return 1

    expected = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    erros: list[str] = []

    for key, cfg in CLASSES.items():
        atual = seed_total_unique(cfg)
        bloco = expected.get(key) or {}
        resumo = bloco.get("summary") or {}
        ref = int(resumo.get("seed_total_unique", -1))
        if ref < 0:
            erros.append(f"{key}: snapshot sem summary.seed_total_unique")
            continue
        if atual != ref:
            erros.append(f"{key}: seed atual={atual}, snapshot={ref}")

    if erros:
        print("PHB seed snapshot: DIVERGÊNCIA")
        for e in erros:
            print(f"  - {e}")
        print(
            "\nSe a mudança no seed_magias.py for intencional, regenere o JSON com o PDF em livros/:\n"
            "  python3 scripts/diff_phb_seed_all_classes.py --json ../docs/diff-phb-seed-all-classes.json"
        )
        return 1

    print("PHB seed snapshot: OK (totais por classe iguais ao docs/diff-phb-seed-all-classes.json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
