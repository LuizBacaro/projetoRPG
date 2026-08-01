#!/usr/bin/env python3
"""Extrai nomes de poderes HA (p.54–97) e MB Cap. 2 para JSON raw.

Requer ``pdftotext`` (poppler) e PDFs em ``livros/`` (locais, fora do git).

Saídas::

    data/_ha_poderes_extract_raw.json
    data/_mb_poderes_extract_raw.json

Depois rode ``build_poderes_herois_arton_catalogo.py`` para gerar o catálogo.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

_ROOT = Path(__file__).resolve().parents[2]
_DATA = Path(__file__).resolve().parents[1] / "app" / "games" / "tormenta" / "data"
_HA_PDF = _ROOT / "livros" / "T20-Herois-de-Arton-v1-1.pdf"
_MB_PDF = _ROOT / "livros" / "Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf"

# Página PDF 1-based = impressa + 2 (HA e JdA v1.3 neste projeto).
_HA_OFFSET = 2


def _pdftotext(pdf: Path, first: int, last: int) -> str:
    if not pdf.is_file():
        raise FileNotFoundError(f"PDF ausente: {pdf}")
    proc = subprocess.run(
        ["pdftotext", "-f", str(first), "-l", str(last), "-layout", str(pdf), "-"],
        check=True,
        capture_output=True,
        text=True,
    )
    return proc.stdout or ""


def _ensure_ha_raw() -> Path:
    """Se o raw já existe (extração rica), mantém; senão gera stub a partir do PDF."""
    out = _DATA / "_ha_poderes_extract_raw.json"
    if out.is_file():
        print(f"OK: {out} já existe — use build_poderes_herois_arton_catalogo.py")
        return out
    # Fallback mínimo: tabelas-resumo via pdftotext (menos preciso que pdfplumber).
    text = _pdftotext(_HA_PDF, 56, 99)
    doc: Dict[str, Any] = {
        "_meta": {
            "fonte": "T20-Herois-de-Arton-v1-1.pdf",
            "metodo": "pdftotext fallback — prefira raw gerado com pdfplumber",
            "nota": "Stub vazio; rode extração completa antes do build.",
        },
        "classe": [],
        "combate": [],
        "destino": [],
        "magia": [],
        "tormenta": [],
        "raca": [],
        "grupo": [],
    }
    # Captura linhas tipo "Nome do Poder" em tabelas 1-18..1-23 (heurística).
    for m in re.finditer(
        r"^(?P<nome>[A-ZÁÉÍÓÚÂÊÔÃÕÇ][A-Za-zÀ-ÿ' \-]{2,40})$",
        text,
        re.MULTILINE,
    ):
        nome = m.group("nome").strip()
        if len(nome.split()) > 6:
            continue
        doc["grupo"].append({"nome": nome, "pagina_referencia": "HA"})
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote stub {out} — complete with pdfplumber extract before production build")
    return out


def _ensure_mb_raw() -> Path:
    out = _DATA / "_mb_poderes_extract_raw.json"
    if out.is_file():
        print(f"OK: {out} já existe")
        return out
    # Tabelas-resumo impressas ~125–127 → PDF ~127–129
    text = _pdftotext(_MB_PDF, 130, 143)
    doc: Dict[str, Any] = {
        "_meta": {
            "fonte": "Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf",
            "metodo": "pdftotext Cap. 2",
        },
        "combate": [],
        "destino": [],
        "magia": [],
        "concedido": [],
        "tormenta": [],
    }
    out.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote placeholder {out} ({len(text)} chars of text available for manual parse)")
    return out


def main() -> int:
    _DATA.mkdir(parents=True, exist_ok=True)
    try:
        _ensure_ha_raw()
        _ensure_mb_raw()
    except FileNotFoundError as e:
        print(e, file=sys.stderr)
        return 1
    print("Próximo: PYTHONPATH=. python3 scripts/build_poderes_herois_arton_catalogo.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
