#!/usr/bin/env python3
"""
Compara listas de magias do PHB (apêndice cap. 11) com seed_magias.py para todas as classes.

Uso:
  python scripts/diff_phb_seed_all_classes.py
  python scripts/diff_phb_seed_all_classes.py --json ../docs/diff-phb-seed-all-classes.json
  python scripts/diff_phb_seed_all_classes.py --class BARDO
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEED_FILE = ROOT / "scripts" / "seed_magias.py"
PHB_PDF = Path(__file__).resolve().parents[2] / "livros" / "D&D3_5_livro_jogador.pdf"

# seed_var, tag em tupla, marcadores PHB (início / fim)
CLASSES: dict[str, dict] = {
    "BARDO": {
        "seed_var": "MAGIAS_BARDO",
        "seed_tag": "BARDO",
        "phb_start": "MAGIAS DE BARDO",
        "phb_end": ("MAGIAS DE CLÉRIGO", "MAGIAS DE CLERIGO"),
        "next_var": "MAGIAS_CLÉRIGO",
    },
    "CLERIGO": {
        "seed_var": "MAGIAS_CLÉRIGO",
        "seed_tag": "CLERIGO",
        "phb_start": "MAGIAS DE CLÉRIGO",
        "phb_end": ("MAGIAS DE DRUIDA", "DOMÍNIOS DE CLÉRIGO", "DOMINIOS DE CLERIGO"),
        "next_var": "MAGIAS_DRUIDA",
    },
    "DRUIDA": {
        "seed_var": "MAGIAS_DRUIDA",
        "seed_tag": "DRUIDA",
        "phb_start": "MAGIAS DE DRUIDA",
        "phb_end": ("MAGIAS DE PALADINO",),
        "next_var": "MAGIAS_PALADINO",
    },
    "PALADINO": {
        "seed_var": "MAGIAS_PALADINO",
        "seed_tag": "PALADINO",
        "phb_start": "MAGIAS DE PALADINO",
        "phb_end": ("NÍVEL DE RANGER", "NIVEL DE RANGER"),
        "next_var": "MAGIAS_RANGER",
    },
    "RANGER": {
        "seed_var": "MAGIAS_RANGER",
        "seed_tag": "RANGER",
        "phb_start": "NÍVEL DE RANGER",
        "phb_end": (
            "MAGIAS DE NÍVEL 0 DE FEITICEIRO E MAGO",
            "MAGIAS DE NIVEL 0 DE FEITICEIRO E MAGO",
        ),
        "next_var": "MAGIAS_MAGO",
    },
    "MAGO": {
        "seed_var": "MAGIAS_MAGO",
        "seed_tag": "MAGO",
        "phb_start": "MAGIAS DE NÍVEL 0 DE FEITICEIRO E MAGO",
        "phb_end": ("As magias apresentadas",),
        "next_var": None,
    },
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^a-z0-9\s]", " ", s.lower())
    return re.sub(r"\s+", " ", s).strip()


# Nome no seed/OCR → chave canônica PHB (normalizada)
ALIASES: dict[str, str] = {
    norm("Mending"): norm("Consertar"),
    norm("Guia"): norm("Orientação"),
    norm("Detectar Veneno"): norm("Detectar Venenos"),
    norm("Ler Magia"): norm("Ler Magias"),
    norm("Abrir / Fechar"): norm("Abrir Fechar"),
    norm("Abrir/Fechar"): norm("Abrir Fechar"),
    norm("Cegueira / Surdez"): norm("Cegueira Surdez"),
    norm("Cegueira/Surdez"): norm("Cegueira Surdez"),
    norm("Mesclar-se às Rochas"): norm("Mesclar se as Rochas"),
    norm("Mesclar-se as Rochas"): norm("Mesclar se as Rochas"),
    norm("Âncora Dimensional"): norm("Ancora Dimensional"),
    norm("Resistir Elementos"): norm("Suportar Elementos"),
    norm("Névoa Obscurecente"): norm("Névoa Obscurescente"),
    norm("Bane"): norm("Maldição Menor"),
    norm("Favor Divino"): norm("Auxílio Divino"),
    norm("Invisibilidade Contra Mortos-Vivos"): norm("Divisibilidade Contra Mortos-Vivos"),
    norm("Invisibilidade Contra Mortos Vivos"): norm("Divisibilidade Contra Mortos-Vivos"),
    norm("Localizar Objeto"): norm("Localizar Objetos"),
    norm("Imobilizar Pessoas"): norm("Imobilizar Pessoa"),
    norm("Constrição"): norm("Emaranhar"),
    norm("Emaranhar"): norm("Emaranhar"),  # druida PHB; não é clérigo
    norm("Proibição de Ação"): norm("Proibição de Ação"),
    norm("Auxilio Divino"): norm("Auxílio Divino"),
    norm("Cotar Ferimentos Leves"): norm("Curar Ferimentos Leves"),
    norm("Corar Ferimentos Moderados"): norm("Curar Ferimentos Moderados"),
    norm("Descanso Tranquilo"): norm("Descanso Tranqüilo"),
    norm("Encontrar Armadilhas"): norm("Encontrar Armadilha"),
    norm("Invocar Criaturas I"): norm("Invocar Criaturas I"),
    norm("Invocar criaturas i"): norm("Invocar Criaturas IX"),
    norm("Enviar Mensage"): norm("Enviar Mensagem"),
    norm("Escudo da Orde"): norm("Escudo da Ordem"),
    norm("Dissipar o Caos Mal Bem Ordem"): norm("Dissipar Caos Mal Bem Ordem"),
    norm("Circulo Magico Contra o Caos Mal Bem Ordem"): norm(
        "Circulo Magico Contra o Caos Mal Bem Ordem"
    ),
    norm("Imunidade a Magia Maior"): norm("Imunidade a Magias"),
    norm("Mensage"): norm("Mensagem"),
    norm("Animar Cordas"): norm("Animar Corda"),
    norm("Clarividencia Clariaudiencia"): norm("Clariaudiencia Clarividencia"),
    norm("Esculpir So"): norm("Esculpir Som"),
    norm("Projetar Image"): norm("Projetar Imagem"),
    norm("Falar com Animais"): norm("Falar Com Animais"),
    norm("Resistencia a Elementos"): norm("Resistência à Elementos"),
    norm("Invisibilidade Contra Animais"): norm("Divisibilidade Contra Animais"),
    norm("Dominar Animal"): norm("Dominar Animais"),
    norm("Controlar a Agua"): norm("Controlar Agua"),
    norm("Controlar Água"): norm("Controlar Agua"),
    norm("Inverter Gravidade"): norm("Inverter a Gravidade"),
    norm("Invocar Aliado da Natureza I"): norm("Invocar Aliado da Natureza IX"),
    norm("Caos Mal Bem Orde"): norm("Detectar Ordem"),
    norm("Protecao Contra o Caos Mal Bem Orde"): norm("Proteção Contra o Caos Mal Bem Ordem"),
    norm("Dissipar o Caos Mal Bem Orde"): norm("Dissipar o Caos Mal Bem Ordem"),
    norm("Raio da Exaustao"): norm("Raio de Exaustao"),
    norm("Raio de Exaustao"): norm("Raio de Exaustao"),
    norm("Convocacao Instantanea de Drawmij"): norm("Convocacao Instantanea de Drawmij"),
    norm("Convocacao Instantanea de Drawmij A"): norm("Convocacao Instantanea de Drawmij"),
    norm("Mao Poderosa de Bigby A"): norm("Mao Poderosa de Bigby"),
    norm("Mao Vigorosa de Bigby A"): norm("Mao Vigorosa de Bigby"),
    norm("Protecao Contra Caos Mal Bem Ordem"): norm("Protecao Contra o Caos Mal Bem Ordem"),
    norm("Flecha Acida de Mel"): norm("Flecha Ácida de Melf"),
    norm("Riso Histerico de Tasha O"): norm("Riso Histérico de Tasha"),
    norm("Encolher Ite"): norm("Encolher Item"),
    norm("Mao Interposta de Bigby A"): norm("Mão Interposta de Bigby"),
    norm("Dificultar DetecçãoM"): norm("Dificultar Detecção"),
    norm("Dissipar Caos / Mal / Bem / Ordem"): norm("Dissipar o Caos Mal Bem Ordem"),
    norm("Proteção Contra o Caos / Mal / Bem / Ordem"): norm(
        "Proteção Contra o Caos Mal Bem Ordem"
    ),
    norm("Proteção Contra o Caos/Mal/Bem/Ordem"): norm(
        "Proteção Contra o Caos Mal Bem Ordem"
    ),
    norm("Tarefa / Missão"): norm("Tarefa Missão"),
    norm("Infligir Ferimentos Moderados em Massa"): norm("Ferimentos Moderados em Massa"),
    norm("Curar Ferimentos Moderados em Massa"): norm("Curar Ferimentos Moderados em Massa"),
}


def canon(name: str) -> str:
    n = norm(name.replace("\n", " "))
    return ALIASES.get(n, n)


def _pdftotext() -> list[str]:
    if not PHB_PDF.is_file():
        raise FileNotFoundError(PHB_PDF)
    proc = subprocess.run(
        ["pdftotext", str(PHB_PDF), "-"],
        capture_output=True,
        text=True,
        check=True,
    )
    return proc.stdout.splitlines()


# Apêndice de listas (pdftotext) começa ~linha 27k; evita sumário no início do PDF.
_APPENDIX_MIN_LINE = 25000


def _find_line(lines: list[str], needle: str, start: int = _APPENDIX_MIN_LINE) -> int:
    hits = [
        i
        for i in range(max(start, 0), len(lines))
        if needle.upper() in lines[i].upper()
    ]
    if not hits:
        raise ValueError(f"Marcador não encontrado: {needle!r}")
    return hits[0]


def _section_bounds(lines: list[str], cfg: dict) -> tuple[int, int]:
    start = _find_line(lines, cfg["phb_start"])
    end = len(lines)
    for marker in cfg["phb_end"]:
        try:
            pos = _find_line(lines, marker, start + 1)
            end = min(end, pos)
        except ValueError:
            continue
    return start, end


def _is_spell_entry_line(line: str) -> bool:
    if ":" not in line:
        return False
    name, desc = line.split(":", 1)
    name, desc = name.strip(), desc.strip()
    if len(name) < 4 or len(name) > 72:
        return False
    if len(desc) < 8:
        return False
    if desc.lower().startswith("como "):
        return False
    low = name.lower()
    if low in {"abjur", "conj", "adiv", "encan", "evoc", "ilus", "necro", "trans", "univ"}:
        return False
    return True


def _parse_level_header(line: str) -> int | None:
    low = line.lower()
    if "preces" in low or "truque" in low:
        return 0
    if "feiticeiro e mago" in low and "nível 0" in low:
        return 0
    mobj = re.search(r"(\d+)\s*[°ºo]?\s*n[ií]vel", line, re.I)
    if mobj:
        return int(mobj.group(1))
    mobj = re.search(r"n[ií]vel\s*(\d+)", line, re.I)
    if mobj:
        return int(mobj.group(1))
    mobj = re.search(r"\b(\d+)\b", line)
    if mobj and "MAGIAS DE" in line.upper():
        return int(mobj.group(1))
    return None


def _load_phb_mago_by_blocks(lines: list[str]) -> dict[int, list[str]]:
    """Feiticeiro/Mago: níveis no PDF saem fora de ordem — usa blocos entre cabeçalhos."""
    start = _find_line(lines, "MAGIAS DE NÍVEL 0 DE FEITICEIRO E MAGO")
    try:
        end = _find_line(lines, "As magias apresentadas", start + 1)
    except ValueError:
        end = len(lines)
    section = lines[start:end]
    headers: list[tuple[int, int]] = []
    for i, raw in enumerate(section):
        line = raw.strip()
        if "FEITICEIRO" not in line.upper() and "MAGO" not in line.upper():
            continue
        lvl = _parse_level_header(line)
        if lvl is not None:
            headers.append((lvl, i))
    if not headers:
        return {}
    out: dict[int, list[str]] = defaultdict(list)
    for idx, (lvl, hstart) in enumerate(headers):
        hend = headers[idx + 1][1] if idx + 1 < len(headers) else len(section)
        for raw in section[hstart + 1 : hend]:
            line = raw.strip()
            if not _is_spell_entry_line(line):
                continue
            name = line.split(":", 1)[0].strip()
            name = re.sub(r"[MFGX]+$", "", name, flags=re.I).strip()
            out[lvl].append(canon(name))
    return out


def load_phb_class(lines: list[str], cfg: dict) -> dict[int, list[str]]:
    if cfg["seed_var"] == "MAGIAS_MAGO":
        return _load_phb_mago_by_blocks(lines)

    start, end = _section_bounds(lines, cfg)
    section = lines[start:end]
    out: dict[int, list[str]] = defaultdict(list)
    current: int | None = None
    skip_school_headers = {
        "abjur",
        "conj",
        "adiv",
        "encan",
        "evoc",
        "ilus",
        "necro",
        "trans",
        "univ",
    }

    for raw in section:
        line = raw.strip()
        if not line or re.fullmatch(r"\d{2,3}", line):
            continue
        if line.startswith("CAPÍTULO") or line.startswith("CAPITULO"):
            continue

        if "MAGIAS DE" in line.upper():
            lvl = _parse_level_header(line)
            if lvl is not None:
                current = lvl
            elif line.upper().strip() in {
                "MAGIAS DE BARDO",
                "MAGIAS DE CLÉRIGO",
                "MAGIAS DE CLERIGO",
                "MAGIAS DE DRUIDA",
                "MAGIAS DE PALADINO",
                "MAGIAS DE RANGER",
            }:
                current = None
            continue

        if current is None or not _is_spell_entry_line(line):
            continue

        name = line.split(":", 1)[0].strip()
        name = re.sub(r"[MFGX]+$", "", name, flags=re.I).strip()
        if not name or len(name) < 3:
            continue
        if norm(name) in skip_school_headers:
            continue
        if name.lower() in {"tros", "dv"}:
            continue

        low_name = name.lower()
        if low_name.replace(" ", "") in {"caos/mal/bem/ordem", "caos/mal/bem/ordem"}:
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


def load_seed_class(cfg: dict) -> tuple[dict[int, list[str]], dict[int, list[str]], list[str]]:
    text = SEED_FILE.read_text(encoding="utf-8")
    var = cfg["seed_var"]
    tag = cfg["seed_tag"]
    next_var = cfg.get("next_var")
    if next_var:
        pat = rf"{re.escape(var)} = \[(.*?)\]\n\n{re.escape(next_var)}"
    else:
        pat = rf"{re.escape(var)} = \[(.*?)\](?:\n\n|\n#)"
    m = re.search(pat, text, re.S)
    if not m:
        raise RuntimeError(f"{var} não encontrado em seed_magias.py")
    block = m.group(1)

    by_level: dict[int, list[str]] = defaultdict(list)
    raw_names: dict[int, list[str]] = defaultdict(list)
    if "CLERIGO" in tag.upper() or "CLÉRIGO" in tag.upper():
        tag_pat = "CL[EÉ]RIGO"
    else:
        tag_pat = re.escape(tag)

    for match in re.finditer(rf"\('([^']*(?:\\'[^']*)*)',\s*(\d+),\s*'{tag_pat}'", block):
        name = match.group(1).replace("\\n", "\n")
        lvl = int(match.group(2))
        raw_names[lvl].append(name)
        by_level[lvl].append(canon(name))

    dupes: list[str] = []
    for lvl, names in raw_names.items():
        counts = Counter(canon(n) for n in names)
        for cname, cnt in sorted(counts.items()):
            if cnt > 1:
                originals = [n for n in names if canon(n) == cname]
                dupes.append(f"nv{lvl}: {cname} ({cnt}x) — {originals}")

    return by_level, raw_names, dupes


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


def print_class_report(class_key: str, report: dict, dupes: list[str]) -> None:
    print("\n" + "=" * 72)
    print(f"CLASSE: {class_key}")
    print("=" * 72)
    has_issue = False
    for lvl in range(10):
        row = report["levels"][str(lvl)]
        miss, ext = row["missing_in_seed"], row["extra_in_seed"]
        if miss or ext or row["phb_count"] != row["seed_count"]:
            has_issue = True
            print(
                f"\nNível {lvl}: PHB={row['phb_count']} | Seed={row['seed_count']} | "
                f"faltam={len(miss)} | extras={len(ext)}"
            )
            for name in miss:
                print(f"  - FALTA: {name}")
            for name in ext:
                print(f"  + EXTRA: {name}")
    if not has_issue:
        print("  OK — níveis 0–9 alinhados (contagens únicas).")
    if dupes:
        print(f"\n  DUPLICATAS no seed ({len(dupes)}):")
        for d in dupes[:30]:
            print(f"    • {d}")
        if len(dupes) > 30:
            print(f"    … e mais {len(dupes) - 30}")
    s = report["summary"]
    print(
        f"\n  Totais: PHB={s['phb_total_unique']} | Seed={s['seed_total_unique']} | "
        f"Faltando={s['total_missing_in_seed']} | Extras={s['total_extra_in_seed']}"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, help="Salvar relatório JSON")
    parser.add_argument("--class", dest="class_key", choices=list(CLASSES) + ["ALL"], default="ALL")
    args = parser.parse_args()

    pdf_lines = _pdftotext()
    full_report: dict = {}

    keys = [args.class_key] if args.class_key != "ALL" else list(CLASSES)
    for key in keys:
        cfg = CLASSES[key]
        phb = load_phb_class(pdf_lines, cfg)
        seed, _, dupes = load_seed_class(cfg)
        report = compare(phb, seed)
        report["duplicates_in_seed"] = dupes
        full_report[key] = report
        print_class_report(key, report, dupes)

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps(full_report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON: {args.json}")


if __name__ == "__main__":
    main()
