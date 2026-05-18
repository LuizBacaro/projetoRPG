#!/usr/bin/env python3
"""
Compara a lista de magias de Clérigo do PHB (apêndice) com MAGIAS_CLÉRIGO em seed_magias.py.

Uso:
  python scripts/diff_clerigo_phb_seed.py
  python scripts/diff_clerigo_phb_seed.py --json report.json
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_FILE = ROOT / "scripts" / "seed_magias.py"
PHB_TEXT = Path(__file__).resolve().parents[2] / "livros" / "D&D3_5_livro_jogador.pdf"


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


# Nome no seed → nome canônico PHB (chave normalizada)
ALIASES: dict[str, str] = {
    norm("Mending"): norm("Consertar"),
    norm("Guia"): norm("Orientação"),
    norm("Detectar Veneno"): norm("Detectar Venenos"),
    norm("Curar Ferimentos Moderados"): norm("Corar Ferimentos Moderados"),
    norm("Descanso Tranquilo"): norm("Descanso Tranqüilo"),
    norm("Encontrar Armadilhas"): norm("Encontrar Armadilha"),
    norm("Resistência a Elementos"): norm("Resistência à Elementos"),
    norm("Cegueira / Surdez"): norm("Cegueira/Surdez"),
    norm("Mesclar-se às Rochas"): norm("Mesclar-se as Rochas"),
    norm("Âncora Dimensional"): norm("Ancora Dimensional"),
    norm("Dissipar Caos / Mal / Bem / Ordem"): norm("Dissipar o Caos/Mal/Bem/Ordem"),
    norm("Círculo Mágico contra o Caos /\nMal / Bem / Ordem"): norm(
        "Circulo Mágico Contra o Caos/Mal/Bem/Ordem"
    ),
    norm("Favor Divino"): norm("Auxílio Divino"),
    norm("Bane"): norm("Maldição Menor"),
    norm("Resistir Elementos"): norm("Suportar Elementos"),
    norm("Invisibilidade Contra Mortos-\nVivos"): norm("Divisibilidade Contra Mortos-Vivos"),
    norm("Proibição de Ação"): norm("Proibição de Ação"),  # extra PHB-adjacent
    norm("Localizar Objeto"): norm("Localizar Objetos"),
    norm("Imobilizar Pessoas"): norm("Imobilizar Pessoa"),
    norm("Tarefa / Missão"): norm("Tarefa/Missão"),
    norm("Infligir Ferimentos Moderados\nem Massa"): norm("Infligir Ferimentos Moderados em Massa"),
    norm("Curar Ferimentos Moderados\nem Massa"): norm("Curar Ferimentos Moderados em Massa"),
    norm("Infligir Ferimentos Moderados em Massa"): norm("Ferimentos Moderados em Massa"),
    norm("Névoa Obscurecente"): norm("Névoa Obscurescente"),
}


def canon(name: str) -> str:
    n = norm(name)
    return ALIASES.get(n, n)


def load_seed() -> dict[int, list[str]]:
    text = SEED_FILE.read_text(encoding="utf-8")
    m = re.search(r"MAGIAS_CL[EÉ]RIGO = \[(.*?)\]\n\nMAGIAS_DRUIDA", text, re.S)
    if not m:
        raise RuntimeError("MAGIAS_CLÉRIGO não encontrado em seed_magias.py")
    block = m.group(1)
    out: dict[int, list[str]] = defaultdict(list)
    for match in re.finditer(r"\('([^']*(?:\\'[^']*)*)',\s*(\d+),\s*'CL", block):
        name = match.group(1).replace("\\n", "\n")
        out[int(match.group(2))].append(canon(name))
    return out


def load_phb() -> dict[int, list[str]]:
    import subprocess

    if not PHB_TEXT.is_file():
        raise FileNotFoundError(PHB_TEXT)

    proc = subprocess.run(
        ["pdftotext", str(PHB_TEXT), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = proc.stdout.splitlines()
    start = next(i for i, ln in enumerate(lines) if "MAGIAS DE CLÉRIGO" in ln)
    end = next(
        i
        for i, ln in enumerate(lines[start:], start)
        if "DOMÍNIOS DE CLÉRIGO" in ln or "DOMINIOS DE CLERIGO" in ln.upper()
    )
    section = lines[start:end]

    out: dict[int, list[str]] = defaultdict(list)
    current: int | None = None

    for raw in section:
        line = raw.strip()
        if not line or line in ("157", "158") or line.startswith("CAPÍTULO"):
            continue

        if "MAGIAS DE" in line and "CLÉRIGO" in line:
            if "preces" in line.lower() or re.search(r"\b0\b", line):
                current = 0
            else:
                mobj = re.search(r"(\d+)", line)
                current = int(mobj.group(1)) if mobj else None
            continue

        if current is None or ":" not in line:
            continue

        name = line.split(":", 1)[0].strip()
        name = re.sub(r"[MFGX]+$", "", name).strip()
        if not name or len(name) < 4:
            continue
        if name.lower() in {"tros", "dv"}:
            continue

        if name.lower().startswith("caos/mal"):
            for part in (
                "Detectar Caos",
                "Detectar Mal",
                "Detectar Bem",
                "Detectar Ordem",
            ):
                out[current].append(canon(part))
            continue

        out[current].append(canon(name))

    return out


def compare(phb: dict[int, list[str]], seed: dict[int, list[str]]) -> dict:
    report: dict = {"levels": {}, "summary": {}}
    total_missing = 0
    total_extra = 0

    for lvl in range(10):
        phb_set = set(phb.get(lvl, []))
        seed_set = set(seed.get(lvl, []))
        missing = sorted(phb_set - seed_set)
        extra = sorted(seed_set - phb_set)
        total_missing += len(missing)
        total_extra += len(extra)
        report["levels"][str(lvl)] = {
            "phb_count": len(phb_set),
            "seed_count": len(seed_set),
            "missing_in_seed": missing,
            "extra_in_seed": extra,
        }

    report["summary"] = {
        "phb_total_unique": sum(len(set(phb.get(i, []))) for i in range(10)),
        "seed_total_unique": sum(len(set(seed.get(i, []))) for i in range(10)),
        "total_missing_in_seed": total_missing,
        "total_extra_in_seed": total_extra,
    }
    return report


def print_report(report: dict) -> None:
    print("=" * 70)
    print("DIFF PHB × SEED — Magias de Clérigo (D&D 3.5)")
    print("=" * 70)
    for lvl in range(10):
        row = report["levels"][str(lvl)]
        print(
            f"\nNível {lvl}: PHB={row['phb_count']} | Seed={row['seed_count']} | "
            f"faltam={len(row['missing_in_seed'])} | extras={len(row['extra_in_seed'])}"
        )
        for name in row["missing_in_seed"]:
            print(f"  - FALTA no seed: {name}")
        for name in row["extra_in_seed"]:
            print(f"  + EXTRA no seed: {name}")

    s = report["summary"]
    print("\n" + "=" * 70)
    print(
        f"Total único PHB: {s['phb_total_unique']} | Seed: {s['seed_total_unique']} | "
        f"Faltando: {s['total_missing_in_seed']} | Extras: {s['total_extra_in_seed']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, help="Salvar relatório JSON")
    args = parser.parse_args()

    phb = load_phb()
    seed = load_seed()
    report = compare(phb, seed)
    print_report(report)

    if args.json:
        args.json.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nRelatório JSON: {args.json}")


if __name__ == "__main__":
    main()
