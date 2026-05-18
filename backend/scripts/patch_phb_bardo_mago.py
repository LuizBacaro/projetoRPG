#!/usr/bin/env python3
"""
Enxuga MAGIAS_BARDO ao PHB e ajusta nomes de MAGO (aliases OCR).

Uso:
  python scripts/patch_phb_bardo_mago.py --dry-run
  python scripts/patch_phb_bardo_mago.py
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

SEED_FILE = Path(__file__).resolve().parent / "seed_magias.py"
sys.path.insert(0, str(SEED_FILE.parent))
from diff_phb_seed_all_classes import (  # noqa: E402
    CLASSES,
    _pdftotext,
    canon,
    load_phb_class,
)


def _py_str(value: str) -> str:
    return "'" + value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n") + "'"


def _format_tuple(t: tuple) -> str:
    nome = _py_str(t[0])
    parts = [nome, str(t[1]), _py_str(t[2])]
    for p in t[3:]:
        if isinstance(p, bool):
            parts.append("True" if p else "False")
        elif p is None or p == "":
            parts.append("''")
        else:
            parts.append(_py_str(str(p)))
    return "    (" + ", ".join(parts) + "),\n"


def _phb_bardo_canon_set() -> set[str]:
    phb = load_phb_class(_pdftotext(), CLASSES["BARDO"])
    out: set[str] = set()
    for lvl in range(10):
        out.update(phb.get(lvl, []))
    return out


def _dedupe_bardo(lst: list[tuple]) -> list[tuple]:
    seen: set[tuple[str, int]] = set()
    out: list[tuple] = []
    for t in lst:
        key = (canon(t[0]), int(t[1]))
        if key in seen:
            continue
        seen.add(key)
        out.append(t)
    return out


def _rebuild_bardo_block(lst: list[tuple]) -> str:
    lst = sorted(lst, key=lambda t: (t[1], canon(t[0])))
    lines: list[str] = []
    cur_lvl: int | None = None
    for t in lst:
        if t[1] != cur_lvl:
            cur_lvl = int(t[1])
            lines.append(f"    # ── Nível {cur_lvl} ──\n")
        lines.append(_format_tuple(t))
    return "".join(lines)


def _extract_bracket_list(texto: str, var: str) -> tuple[str, int, int]:
    header = f"{var} = ["
    idx = texto.index(header)
    start = idx + len(header) - 1  # position of '['
    depth = 0
    in_str: str | None = None
    escape = False
    for i in range(start, len(texto)):
        ch = texto[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == in_str:
                in_str = None
            continue
        if ch in ("'", '"'):
            in_str = ch
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                return texto[start : i + 1], start, i + 1
    raise RuntimeError(f"Lista {var} não fechada")


def trim_bardo(texto: str, phb_all: set[str]) -> tuple[str, int]:
    list_lit, list_start, list_end = _extract_bracket_list(texto, "MAGIAS_BARDO")
    original: list[tuple] = ast.literal_eval(list_lit)
    before = len(original)
    kept = [t for t in original if canon(t[0]) in phb_all and t[0] != "NOME DA MAGIA"]
    kept = _dedupe_bardo(kept)
    removed = before - len(kept)
    new_block = _rebuild_bardo_block(kept)
    header_pos = texto.index("MAGIAS_BARDO = [")
    texto = texto[:header_pos] + "MAGIAS_BARDO = [\n" + new_block + "]" + texto[list_end:]
    return texto, removed


def aplicar(texto: str) -> tuple[str, dict]:
    phb_all = _phb_bardo_canon_set()
    texto, removed = trim_bardo(texto, phb_all)
    stats = {"bardo_removed": removed}

    for old, new in [
        ("Raio da Exaustão", "Raio de Exaustão"),
        ("Proteção Contra Caos / Mal / Bem / Ordem", "Proteção Contra o Caos / Mal / Bem / Ordem"),
    ]:
        texto = texto.replace(f"('{old}',", f"('{new}',")

    return texto, stats


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    texto = SEED_FILE.read_text(encoding="utf-8")
    novo, stats = aplicar(texto)

    if novo == texto:
        print("Nenhuma alteração necessária.")
        return

    ast.parse(novo)

    if args.dry_run:
        print(f"Bardo: removeriam {stats['bardo_removed']} entradas (dry-run)")
        return

    SEED_FILE.write_text(novo, encoding="utf-8")
    print(f"Bardo: removidas {stats['bardo_removed']} entradas; Mago: renomes PHB")
    print(f"Salvo em {SEED_FILE}")


if __name__ == "__main__":
    main()
