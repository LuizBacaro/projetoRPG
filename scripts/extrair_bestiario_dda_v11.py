#!/usr/bin/env python3
"""Extrai bestiário Deuses de Arton v1.1 Cap. 4 (pp. impressas 252–315).

Uso local (PDF em ``livros/``, não versionado no git):

  python3 scripts/extrair_bestiario_dda_v11.py \\
    --pdf livros/T20-Deuses-de-Arton-v1-1.pdf \\
    --out backend/app/games/tormenta/data/bestiario_dda_v11.json

Inventário: Tabela de Ameaças por ND (impressa 319 = PDF 321), grupos
Abissais|Aspectos|Celestiais|Fadas|Gênios|Gigantes.
Offset: PDF_index = impressa + 2.
Gera só metadados mecânicos + remissão; revisão humana antes do commit.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

PDF_OFFSET = 2  # impressa = PDF - 2
TABELA_PDF = 321
BLOCOS_PDF_INI = 254  # impressa 252
BLOCOS_PDF_FIM = 317  # impressa 315

GRUPOS_OK = {
    "Abissais",
    "Aspectos",
    "Celestiais",
    "Fadas",
    "Gênios",
    "Gigantes",
}

ATTR_LABELS = {
    "For": "for",
    "Des": "des",
    "Con": "con",
    "Int": "int",
    "Sab": "sab",
    "Car": "car",
}


def slugify(nome: str) -> str:
    s = unicodedata.normalize("NFKD", nome)
    s = "".join(c for c in s if not unicodedata.combining(c))
    s = s.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "criatura"


def parse_nd(raw: str) -> Tuple[Optional[float], str]:
    s = (raw or "").strip().replace(",", ".")
    if not s:
        return None, ""
    su = s.upper()
    if su in ("S", "S+", "?"):
        return None, su if su != "?" else "?"
    if "/" in s:
        a, b = s.split("/", 1)
        return float(a) / float(b), s
    nd = float(s)
    return nd, str(int(nd)) if nd == int(nd) else s


def mod_to_score(mod: int) -> int:
    return 10 + 2 * int(mod)


def pdftotext_pages(pdf: Path, first: int, last: int) -> str:
    proc = subprocess.run(
        ["pdftotext", "-layout", "-f", str(first), "-l", str(last), str(pdf), "-"],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr or "pdftotext falhou")
    return proc.stdout or ""


def _entry(nome: str, grupo: str, nd_raw: str) -> Optional[Dict[str, Any]]:
    nome = re.sub(r"\s+", " ", nome).strip(" .·•-")
    grupo = grupo.strip()
    if grupo not in GRUPOS_OK:
        return None
    if not nome or nome.lower().startswith("avatar"):
        return None
    nd, rotulo = parse_nd(nd_raw)
    slug = slugify(nome)
    item: Dict[str, Any] = {
        "slug": slug,
        "nome": nome,
        "nd_rotulo": rotulo,
        "grupo": grupo,
        "fonte": "dda_v11",
        "pagina_referencia": "dda v1.1 p.252",
        "descricao_curta": f"Ameaça divina ({grupo}).",
    }
    if nd is not None:
        item["nd"] = nd
        item["nivel"] = max(1, int(math.ceil(nd)))
    else:
        item["nd"] = None
        item["nivel"] = 1
    return item


def _half_re() -> str:
    grupos = "|".join(re.escape(g) for g in sorted(GRUPOS_OK, key=len, reverse=True))
    # Inclui Perigos/Avatares na regex da linha para não quebrar o split em 2 cols,
    # mas _entry descarta.
    grupos_all = grupos + r"|Perigos|Avatares"
    return (
        rf"([A-Za-zÀ-ú][A-Za-zÀ-ú0-9'’\- ]+?)\s+"
        rf"({grupos_all})\s+"
        rf"(\?|S\+?|1/4|1/2|\d+)"
    )


def extrair_tabela_ameacas(texto: str) -> List[Dict[str, Any]]:
    half = _half_re()
    line_re = re.compile(rf"^{half}\s+{half}\s*$")
    single_re = re.compile(rf"^{half}\s*$")
    out: List[Dict[str, Any]] = []
    for line in texto.splitlines():
        raw = line.strip()
        if not raw or raw.startswith("Tabela") or raw.startswith("Criatura"):
            continue
        if "Ameaças Divinas" in raw or re.fullmatch(r"\d+", raw):
            continue
        m = line_re.match(raw)
        if m:
            for i in (1, 4):
                e = _entry(m.group(i), m.group(i + 1), m.group(i + 2))
                if e:
                    out.append(e)
            continue
        m = single_re.match(raw)
        if m:
            e = _entry(m.group(1), m.group(2), m.group(3))
            if e:
                out.append(e)
    seen: set[str] = set()
    dedup: List[Dict[str, Any]] = []
    for c in out:
        if c["slug"] in seen:
            continue
        seen.add(c["slug"])
        dedup.append(c)
    return dedup


def _grab_int(text: str, pattern: str, default: int = 0) -> int:
    m = re.search(pattern, text, flags=re.I)
    if not m:
        return default
    try:
        return int(m.group(1).replace("+", ""))
    except ValueError:
        return default


def parse_stats_window(window: str, base: Dict[str, Any], pagina: int) -> Dict[str, Any]:
    item = dict(base)
    item["pagina_referencia"] = f"dda v1.1 p.{pagina}"
    item["fonte"] = "dda_v11"

    tipo_m = re.search(
        r"\b(Animal|Humanoide|Monstro|Esp[ií]rito|Construto|Morto-vivo|Drag[aã]o|"
        r"Fada|Elemental)\b"
        r"(?:\s*\([^)]+\))?\s+(\S+)",
        window,
        flags=re.I,
    )
    if tipo_m:
        tipo = tipo_m.group(1)
        tipo = (
            tipo.replace("Espirito", "Espírito")
            .replace("Dragao", "Dragão")
            .replace("Fada", "Espírito")
        )
        # Normaliza capitalização
        tipo = tipo[0].upper() + tipo[1:] if tipo else "Criatura"
        item["tipo_criatura"] = tipo
        item["tamanho"] = tipo_m.group(2)[:40]
    else:
        item.setdefault("tipo_criatura", "Criatura")
        item.setdefault("tamanho", "Médio")

    item["iniciativa"] = _grab_int(window, r"Iniciativa\s*([+-]?\d+)")
    item["percepcao"] = _grab_int(window, r"Percep[cç][aã]o\s*([+-]?\d+)")
    item["ca"] = _grab_int(window, r"Defesa\s*(\d+)", 10)
    item["pv_max"] = max(1, _grab_int(window, r"Pontos de Vida\s*(\d+)", 1))
    item["pa_max"] = max(0, _grab_int(window, r"Pontos de Mana\s*(\d+)", 0))
    item["fort_total"] = _grab_int(window, r"Fort(?:itude)?\s*([+-]?\d+)")
    item["ref_total"] = _grab_int(window, r"Ref(?:lexos)?\s*([+-]?\d+)")
    item["von_total"] = _grab_int(window, r"Von(?:tade)?\s*([+-]?\d+)")

    desl_m = re.search(r"Deslocamento\s+([^\n]+)", window, flags=re.I)
    if desl_m:
        item["deslocamento"] = re.split(r"[.;]", desl_m.group(1).strip())[0].strip()[:80]
    else:
        item["deslocamento"] = "9m"

    rd_m = re.search(r"(?:redu[cç][aã]o de dano|RD)\s+(\d+[^\n,;]*)", window, flags=re.I)
    item["rd"] = rd_m.group(1).strip()[:80] if rd_m else ""

    nulos: List[str] = []
    attrs = {k: 10 for k in ("for", "des", "con", "int", "sab", "car")}
    for lab, key in ATTR_LABELS.items():
        m = re.search(rf"{lab}\s+([+−\-–]?\d+|—)", window)
        if not m:
            continue
        val = m.group(1).replace("−", "-").replace("–", "-")
        if val in ("—", "-"):
            nulos.append(key)
        else:
            try:
                attrs[key] = mod_to_score(int(val))
            except ValueError:
                pass
    for k, v in attrs.items():
        item[f"{k}_valor"] = v
    item["atributos_nulos"] = nulos

    ataques: List[Dict[str, str]] = []
    for m in re.finditer(
        r"(?:Corpo a Corpo|À Dist[aâ]ncia)\s+(.+?)(?:\n[A-ZÀ-Ú]|\n\s*For\s|\nPer[ií]cias|\nEquipamento|\nTesouro|$)",
        window,
        flags=re.I | re.S,
    ):
        chunk = m.group(1)
        for am in re.finditer(
            r"([A-Za-zÀ-ú][A-Za-zÀ-ú0-9'’\-\[\]\s]{0,50}?)\s+([+-]\d+)\s*\(([^)]+)\)",
            chunk,
        ):
            nome_atq = re.sub(r"\s+", " ", am.group(1)).strip(" []")
            if len(nome_atq) < 2:
                continue
            dano = am.group(3).strip()
            ataques.append(
                {
                    "nome": nome_atq[:120],
                    "bonus_ataque": am.group(2),
                    "dano": dano[:80],
                }
            )
    if not ataques:
        for am in re.finditer(
            r"([A-Za-zÀ-ú][A-Za-zÀ-ú0-9'’\-]{2,40})\s+([+-]\d+)\s*\((\d*d\d[^)]*)\)",
            window,
        ):
            nome_atq = am.group(1).strip()
            if nome_atq.lower() in ("fort", "ref", "von", "defesa"):
                continue
            ataques.append(
                {
                    "nome": nome_atq[:120],
                    "bonus_ataque": am.group(2),
                    "dano": am.group(3)[:80],
                }
            )
            if len(ataques) >= 4:
                break
    seen: set[tuple[str, str]] = set()
    atq_out: List[Dict[str, str]] = []
    for a in ataques:
        key = (a["nome"].lower(), a["bonus_ataque"])
        if key in seen:
            continue
        seen.add(key)
        atq_out.append(a)
    item["ataques"] = atq_out[:6]
    rot = item.get("nd_rotulo") or item.get("nd") or "?"
    item["descricao_curta"] = (
        f"{item.get('tipo_criatura', 'Criatura')} {item.get('tamanho', '')}, "
        f"ND {rot}."
    ).strip()
    return item


def column_stream(page_text: str, side: str, mid: int = 55) -> str:
    lines: List[str] = []
    for ln in page_text.splitlines():
        if len(ln) <= mid:
            left, right = ln.rstrip(), ""
        else:
            left, right = ln[:mid].rstrip(), ln[mid:].rstrip()
        lines.append(left if side == "left" else right)
    return "\n".join(lines)


def _nd_pat(sk: Dict[str, Any]) -> str:
    rot = str(sk.get("nd_rotulo") or "").strip()
    if rot in ("S", "S+", "?"):
        return re.escape(rot)
    if rot:
        return re.escape(rot)
    return r"(?:\?|S\+?|1/4|1/2|\d+)"


def enriquecer_com_blocos(
    skeleton: List[Dict[str, Any]], texto_blocos: str
) -> List[Dict[str, Any]]:
    pages = texto_blocos.split("\x0c")
    found: Dict[str, Tuple[str, int]] = {}

    for i, page in enumerate(pages):
        pagina = (BLOCOS_PDF_INI + i) - PDF_OFFSET
        left = column_stream(page, "left")
        right = column_stream(page, "right")
        sk_sorted = sorted(skeleton, key=lambda s: len(s["nome"]), reverse=True)
        for sk in sk_sorted:
            if sk["slug"] in found:
                continue
            nome = sk["nome"]
            ndp = _nd_pat(sk)
            m = re.search(
                rf"{re.escape(nome)}\s+ND\s+{ndp}\b",
                page,
                flags=re.I,
            )
            if not m:
                # ND pode estar na coluna vizinha (layout 2 col)
                m = re.search(
                    rf"{re.escape(nome)}\s*\n[^\n]*?ND\s+{ndp}\b",
                    page,
                    flags=re.I | re.S,
                )
            if not m:
                m = re.search(
                    rf"(?<![A-Za-zÀ-ú]){re.escape(nome)}\b",
                    page,
                    flags=re.I,
                )
                if m:
                    window_probe = page[m.start() : m.start() + 400]
                    if not re.search(r"\bND\s+", window_probe, flags=re.I):
                        continue
                    if not re.search(r"Iniciativa|Defesa|Pontos de Vida", window_probe, flags=re.I):
                        # pode ser prosa introdutória — exige stats próximos
                        window_probe2 = page[m.start() : m.start() + 1200]
                        if not re.search(r"Iniciativa|Defesa", window_probe2, flags=re.I):
                            continue
            if not m:
                continue
            if m.start() > 0 and page[m.start() - 1].isalnum():
                continue
            line_start = page.rfind("\n", 0, m.start()) + 1
            col_pos = m.start() - line_start
            side = "left" if col_pos < 55 else "right"
            col_txt = left if side == "left" else right
            m2 = re.search(rf"(?<![A-Za-zÀ-ú]){re.escape(nome)}\b", col_txt, flags=re.I)
            if m2:
                window = col_txt[m2.start() : m2.start() + 2800]
            else:
                window = page[m.start() : m.start() + 2800]
            if not re.search(r"\bND\s+", window[:120], flags=re.I):
                window = f"{nome} ND {sk.get('nd_rotulo', sk.get('nd') or '?')}\n{window}"
            found[sk["slug"]] = (window, pagina)

    out: List[Dict[str, Any]] = []
    for sk in skeleton:
        if sk["slug"] in found:
            window, pagina = found[sk["slug"]]
            out.append(parse_stats_window(window, sk, pagina))
        else:
            nd = sk.get("nd")
            nd_f = float(nd) if isinstance(nd, (int, float)) else 5.0
            out.append(
                {
                    **sk,
                    "tipo_criatura": "Criatura",
                    "tamanho": "Médio",
                    "for_valor": 10,
                    "des_valor": 10,
                    "con_valor": 10,
                    "int_valor": 10,
                    "sab_valor": 10,
                    "car_valor": 10,
                    "atributos_nulos": [],
                    "pv_max": max(1, int(20 + 20 * nd_f)),
                    "pa_max": 0,
                    "ca": max(10, int(12 + nd_f)),
                    "iniciativa": 0,
                    "deslocamento": "9m",
                    "fort_total": 0,
                    "ref_total": 0,
                    "von_total": 0,
                    "rd": "",
                    "ataques": [],
                    "fonte": "dda_v11",
                }
            )

    def sort_key(r: Dict[str, Any]) -> tuple:
        nd = r.get("nd")
        if isinstance(nd, (int, float)):
            return (0, float(nd), str(r.get("nome") or "").lower())
        return (1, str(r.get("nd_rotulo") or "Z"), str(r.get("nome") or "").lower())

    out.sort(key=sort_key)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if not args.pdf.is_file():
        raise SystemExit(f"PDF não encontrado: {args.pdf}")

    skeleton = extrair_tabela_ameacas(pdftotext_pages(args.pdf, TABELA_PDF, TABELA_PDF))
    texto_blocos = pdftotext_pages(args.pdf, BLOCOS_PDF_INI, BLOCOS_PDF_FIM)
    criaturas = enriquecer_com_blocos(skeleton, texto_blocos)

    payload = {
        "versao": 1,
        "fonte": "dda_v11",
        "nota": (
            "Cap.4 Ameaças Divinas pp.252–315 (Deuses de Arton v1.1); "
            "metadados mecânicos + remissão; sem texto longo."
        ),
        "criaturas": criaturas,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    com_atq = sum(1 for c in criaturas if c.get("ataques"))
    com_stats = sum(1 for c in criaturas if (c.get("pv_max") or 0) > 1 and c.get("ca", 10) != 10)
    print(
        f"OK: {len(criaturas)} criaturas "
        f"({com_atq} com ataques, {com_stats} com PV/Defesa parseados) → {args.out}"
    )
    por_grupo: Dict[str, int] = {}
    for c in criaturas:
        g = str(c.get("grupo") or "?")
        por_grupo[g] = por_grupo.get(g, 0) + 1
    print("grupos:", por_grupo)


if __name__ == "__main__":
    main()
