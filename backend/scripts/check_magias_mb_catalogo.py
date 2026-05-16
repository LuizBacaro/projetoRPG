#!/usr/bin/env python33
"""Checagens leves de qualidade sobre `magias_mb_catalogo.json` (duplicatas, slugs, campos mínimos)."""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CATALOGO = _ROOT / "app" / "games" / "tormenta" / "data" / "magias_mb_catalogo.json"


def main() -> int:
    if not _CATALOGO.is_file():
        print(f"ERRO: catálogo não encontrado: {_CATALOGO}", file=sys.stderr)
        return 2
    data = json.loads(_CATALOGO.read_text(encoding="utf-8"))
    itens = data.get("itens")
    if not isinstance(itens, list):
        print("ERRO: JSON sem lista `itens`.", file=sys.stderr)
        return 2

    erros: list[str] = []
    avisos: list[str] = []
    by_pair: defaultdict[tuple[str, str], list[str]] = defaultdict(list)
    slugs: list[str] = []

    for i, row in enumerate(itens):
        if not isinstance(row, dict):
            erros.append(f"item[{i}] não é objeto")
            continue
        slug = str(row.get("slug") or "").strip()
        nome = str(row.get("nome") or "").strip()
        tipo = str(row.get("tipo") or "").strip().lower()
        if len(slug) > 80:
            erros.append(f"slug longo (>80): {slug[:40]}…")
        if not slug:
            erros.append(f"item[{i}] sem slug")
        if not nome:
            erros.append(f"slug {slug!r} sem nome")
        if tipo not in ("arcana", "divina"):
            erros.append(f"{slug!r}: tipo inválido {tipo!r}")
        try:
            c = int(row["circulo"])
            if c < 0 or c > 20:
                erros.append(f"{slug!r}: circulo fora 0..20")
        except (KeyError, TypeError, ValueError):
            erros.append(f"{slug!r}: circulo ausente ou inválido")
        slugs.append(slug)
        if nome and tipo in ("arcana", "divina"):
            key = (nome.lower(), tipo)
            by_pair[key].append(slug)

    dup_slugs = [s for s, n in Counter(slugs).items() if n > 1 and s]
    for s in sorted(dup_slugs):
        erros.append(f"slug duplicado no JSON: {s}")

    for (nome_l, tipo), lst in sorted(by_pair.items()):
        if len(lst) > 1:
            avisos.append(f"nome+tipo repetidos ({len(lst)}): {nome_l!r} / {tipo} → {', '.join(lst[:5])}")

    meta = data.get("meta")
    if not isinstance(meta, dict):
        avisos.append("`meta` ausente ou não-objeto")

    print(f"Catálogo: {_CATALOGO}")
    print(f"Total de itens: {len(itens)}")
    print(f"Avisos (nome+tipo): {len(avisos)}")
    for a in avisos[:30]:
        print(f"  AVISO: {a}")
    if len(avisos) > 30:
        print(f"  … +{len(avisos) - 30} avisos")
    print(f"Erros: {len(erros)}")
    for e in erros[:50]:
        print(f"  ERRO: {e}")
    if len(erros) > 50:
        print(f"  … +{len(erros) - 50} erros")

    return 1 if erros else 0


if __name__ == "__main__":
    raise SystemExit(main())
