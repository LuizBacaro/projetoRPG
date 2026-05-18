#!/usr/bin/env python3
"""Gera backend/data/dnd5e_spell_translations_pt.json a partir do Foundry dnd5e-pt-br."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.games.dnd5e.data.foundry_spells import extrair_traducao_entry

ROOT = Path(__file__).resolve().parents[1]
FOUNDRY = ROOT / "data" / "dnd5e_foundry_spells_pt.json"
OUT = ROOT / "data" / "dnd5e_spell_translations_pt.json"


def main() -> None:
    if not FOUNDRY.is_file():
        print(f"Arquivo ausente: {FOUNDRY}", flush=True)
        print("Baixe: decito/dnd5e-pt-br compendium/dnd5e.spells.json", flush=True)
        raise SystemExit(1)

    entries = json.loads(FOUNDRY.read_text(encoding="utf-8")).get("entries") or {}
    out: dict[str, dict[str, str]] = {}
    com_desc = 0
    for key, entry in entries.items():
        slug, data = extrair_traducao_entry(key, entry)
        if not slug or not data.get("nome"):
            continue
        if data.get("descricao"):
            com_desc += 1
        out[slug] = data

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Gerado {OUT} — {len(out)} magias ({com_desc} com descrição PT).")


if __name__ == "__main__":
    main()
