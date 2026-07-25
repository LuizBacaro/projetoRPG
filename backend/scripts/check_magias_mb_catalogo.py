#!/usr/bin/env python3
"""Checagens de qualidade sobre `magias_mb_catalogo.json` (catálogo Tormenta 20 v1.3).

Fonte canónica: Edição Jogo do Ano v1.3 (círculos 1–5). O snapshot MB legado
(~707, círculos 0–9) vive em `magias_mb_catalogo.legacy_mb.json` e não é
validado por este script.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
_CATALOGO = _ROOT / "app" / "games" / "tormenta" / "data" / "magias_mb_catalogo.json"

# Volume esperado: listas arcana+divina v1.3 (entradas tipadas; ~141 descrições únicas).
_TOTAL_MIN = 150
_TOTAL_MAX = 280


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
            if c < 1 or c > 5:
                erros.append(f"{slug!r}: circulo {c} fora de 1..5 (catálogo v1.3)")
        except (KeyError, TypeError, ValueError):
            erros.append(f"{slug!r}: circulo ausente ou inválido")
        if str(row.get("nome") or "").startswith("[Stub]") or slug.startswith("stub_"):
            erros.append(f"stub de CI remanescente: {slug!r}")
        slugs.append(slug)
        if nome and tipo in ("arcana", "divina"):
            key = (nome.lower(), tipo)
            by_pair[key].append(slug)

    dup_slugs = [s for s, n in Counter(slugs).items() if n > 1 and s]
    for s in sorted(dup_slugs):
        erros.append(f"slug duplicado no JSON: {s}")

    for (nome_l, tipo), lst in sorted(by_pair.items()):
        if len(lst) > 1:
            avisos.append(
                f"nome+tipo repetidos ({len(lst)}): {nome_l!r} / {tipo} → {', '.join(lst[:5])}"
            )

    meta = data.get("meta")
    if not isinstance(meta, dict):
        avisos.append("`meta` ausente ou não-objeto")

    com_escola = sum(1 for row in itens if isinstance(row, dict) and row.get("escola"))
    n = len(itens)
    if n < _TOTAL_MIN or n > _TOTAL_MAX:
        erros.append(
            f"total {n} fora da faixa v1.3 esperada ({_TOTAL_MIN}–{_TOTAL_MAX})"
        )
    if com_escola < n * 0.8:
        avisos.append(
            f"cobertura escola baixa: {com_escola}/{n} "
            "(v1.3: listas p.174–177 devem trazer escola)"
        )

    # amostras canónicas do livro
    nomes = {
        str(row.get("nome") or "").strip().lower()
        for row in itens
        if isinstance(row, dict)
    }
    for amostra in ("abençoar alimentos", "adaga mental", "bola de fogo", "curar ferimentos"):
        if amostra not in nomes:
            erros.append(f"magia v1.3 ausente: {amostra!r}")

    print(f"Catálogo: {_CATALOGO}")
    print(f"Total de itens: {n} (com escola: {com_escola}) — esperado v1.3 {_TOTAL_MIN}–{_TOTAL_MAX}")
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
