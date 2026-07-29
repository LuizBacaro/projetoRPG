#!/usr/bin/env python3
"""Extrai rascunhos do Livro dos Monstros 3.5 e valida bestiario_mm35.json.

O PDF é escaneado (OCR fraco). Este script:
1. Opcionalmente gera um rascunho de nomes a partir do sumário (`--draft`).
2. Valida o JSON curado do repositório (`--validate`, padrão).

Uso (raiz do repo):
  python3 scripts/extrair_bestiario_mm35.py --validate
  python3 scripts/extrair_bestiario_mm35.py --draft --pdf livros/dd-3e-livro-dos-monstros-3-5.pdf
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_JSON = ROOT / "backend" / "app" / "games" / "dnd35" / "data" / "bestiario_mm35.json"
DEFAULT_PDF = ROOT / "livros" / "dd-3e-livro-dos-monstros-3-5.pdf"


def validar(path: Path) -> int:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("criaturas") or []
    if len(rows) < 300:
        print(f"ERRO: esperado ≥300 criaturas (lotes 0–4), got {len(rows)}", file=sys.stderr)
        return 1
    slugs = [str(r.get("slug") or "").strip() for r in rows]
    if len(slugs) != len(set(slugs)):
        print("ERRO: slugs duplicados", file=sys.stderr)
        return 1
    erros = 0
    for r in rows:
        slug = r.get("slug")
        if not slug or not r.get("nome"):
            print(f"ERRO: entrada sem slug/nome: {r!r}", file=sys.stderr)
            erros += 1
            continue
        if r.get("fonte") != "mm35":
            print(f"AVISO: {slug} sem fonte=mm35", file=sys.stderr)
        if not r.get("pagina_referencia"):
            print(f"ERRO: {slug} sem pagina_referencia", file=sys.stderr)
            erros += 1
        # Espécie-pai (catálogo) pode ter nd nulo; idades importáveis precisam de stats.
        if r.get("nd") is None and not r.get("categoria_idade") and r.get("especie_pai") is None:
            # pai de família
            continue
        for campo in ("ca", "toque", "surpresa", "hp_maximo"):
            if r.get(campo) is None:
                print(f"ERRO: {slug} sem {campo}", file=sys.stderr)
                erros += 1
        if int(r.get("ca") or 0) < int(r.get("toque") or 0):
            print(f"AVISO: {slug} CA < toque (revisar)", file=sys.stderr)
    dragao_idades = [
        r for r in rows if r.get("especie_pai") == "dragao-azul" and r.get("categoria_idade")
    ]
    if len(dragao_idades) < 12:
        print(f"ERRO: esperado 12 idades de dragão-azul, got {len(dragao_idades)}", file=sys.stderr)
        erros += 1
    vermelho = [
        r for r in rows if r.get("especie_pai") == "dragao-vermelho" and r.get("categoria_idade")
    ]
    if len(vermelho) < 12:
        print(f"ERRO: esperado 12 idades de dragão-vermelho, got {len(vermelho)}", file=sys.stderr)
        erros += 1
    pais_dragao = [
        r for r in rows
        if r.get("tipo_criatura") == "Dragão" and r.get("nd") is None and not r.get("categoria_idade")
    ]
    if len(pais_dragao) < 10:
        print(f"ERRO: esperado ≥10 espécies-pai de dragão, got {len(pais_dragao)}", file=sys.stderr)
        erros += 1
    if erros:
        print(f"Falhou com {erros} erro(s).", file=sys.stderr)
        return 1
    print(f"OK: {len(rows)} criaturas em {path}")
    return 0


def draft_from_pdf(pdf: Path, out: Path) -> int:
    if not pdf.is_file():
        print(f"PDF ausente: {pdf}", file=sys.stderr)
        return 1
    # Sumário aproximado (páginas 4–6 do PDF)
    try:
        proc = subprocess.run(
            ["pdftotext", "-f", "4", "-l", "6", "-layout", str(pdf), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError) as e:
        print(f"Falha pdftotext: {e}", file=sys.stderr)
        return 1
    nomes = []
    for line in proc.stdout.splitlines():
        m = re.match(r"^([A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ'’\- ]{2,40})\s+\d{1,3}\s*$", line.strip())
        if m:
            nomes.append(m.group(1).strip())
    out.write_text(
        json.dumps({"rascunho_nomes": nomes, "total": len(nomes)}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    print(f"Rascunho: {len(nomes)} nomes → {out}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--validate", action="store_true", default=True)
    ap.add_argument("--draft", action="store_true")
    ap.add_argument("--json", type=Path, default=DEFAULT_JSON)
    ap.add_argument("--pdf", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--draft-out", type=Path, default=ROOT / "scripts" / "out_bestiario_mm35_draft.json")
    args = ap.parse_args()
    if args.draft:
        return draft_from_pdf(args.pdf, args.draft_out)
    return validar(args.json)


if __name__ == "__main__":
    raise SystemExit(main())
