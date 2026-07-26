#!/usr/bin/env python3
"""Extrai bestiário T20 v1.3 (Tabela 7-1 + blocos pp. 286–316).

Uso local (PDF em ``livros/``, não versionado no git):

  python3 scripts/extrair_bestiario_t20_v13.py \\
    --pdf livros/Tormenta20-Edicao-Jogo-do-Ano-v1.3.pdf \\
    --out backend/app/games/tormenta/data/bestiario_v13.json

Gera só metadados mecânicos + remissão de página; revisão humana antes do commit.
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

PDF_OFFSET = 6
TABELA_PDF = 291
BLOCOS_PDF_INI = 292
BLOCOS_PDF_FIM = 322

STUB_ALIASES = {
    "lobo": ["lobo"],
    "esqueleto": ["esqueleto"],
    "zumbi": ["zumbi"],
    "goblin-salteador": ["goblin"],
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


def parse_nd(raw: str) -> Tuple[float, str]:
    s = (raw or "").strip().replace(",", ".")
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


def _entry(nome: str, grupo: str, nd_raw: str) -> Dict[str, Any]:
    nome = re.sub(r"\s+", " ", nome).strip(" .·•-")
    # correções tipográficas conhecidas
    if nome.lower().startswith("fintroll"):
        nome = "Finntroll" + nome[8:]
    nd, rotulo = parse_nd(nd_raw)
    slug = slugify(nome)
    item: Dict[str, Any] = {
        "slug": slug,
        "nome": nome,
        "nd": nd,
        "nd_rotulo": rotulo,
        "grupo": grupo.strip() or None,
        "nivel": max(1, int(math.ceil(nd))),
        "pagina_referencia": "v1.3 p.285",
        "descricao_curta": f"Ameaça do bestiário Tormenta 20 ({grupo.strip() or 'geral'}).",
    }
    if slug in STUB_ALIASES:
        item["aliases"] = list(STUB_ALIASES[slug])
    return item


def extrair_tabela_7_1(texto: str) -> List[Dict[str, Any]]:
    """Tabela em duas colunas: Nome Grupo ND | Nome Grupo ND."""
    out: List[Dict[str, Any]] = []
    # Cada metade: nome (palavras) + grupo + ND
    half = (
        r"([A-Za-zÀ-ú][A-Za-zÀ-ú0-9'’\- ]+?)\s+"
        r"(Ermos|Masmorras|Sszzaazitas|Duyshidakk|Reino dos Mortos|Puristas|Tormenta|Dragões|Trolls nobres)\s+"
        r"(1/4|1/2|\d+)"
    )
    line_re = re.compile(rf"^{half}\s+{half}\s*$")
    single_re = re.compile(rf"^{half}\s*$")
    for line in texto.splitlines():
        raw = line.strip()
        if not raw or raw.startswith("Tabela") or raw.startswith("Criatura"):
            continue
        m = line_re.match(raw)
        if m:
            out.append(_entry(m.group(1), m.group(2), m.group(3)))
            out.append(_entry(m.group(4), m.group(5), m.group(6)))
            continue
        m = single_re.match(raw)
        if m:
            out.append(_entry(m.group(1), m.group(2), m.group(3)))
    # Dedup
    seen = set()
    dedup = []
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
    item["pagina_referencia"] = f"v1.3 p.{pagina}"

    tipo_m = re.search(
        r"\b(Animal|Humanoide|Monstro|Esp[ií]rito|Construto|Morto-vivo|Drag[aã]o)\b"
        r"(?:\s*\([^)]+\))?\s+(\S+)",
        window,
        flags=re.I,
    )
    if tipo_m:
        tipo = tipo_m.group(1)
        tipo = tipo.replace("Espirito", "Espírito").replace("Dragao", "Dragão")
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

    rd_m = re.search(r"\bRD\s+([^,;\n]+)", window, flags=re.I)
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
            r"([A-Za-zÀ-ú][A-Za-zÀ-ú0-9'’\-\s]{0,40}?)\s+([+-]\d+)\s*\(([^)]+)\)",
            chunk,
        ):
            nome_atq = am.group(1).strip()
            if len(nome_atq) < 2:
                continue
            dano = am.group(3).strip()
            critico = ""
            cm = re.search(r"(?:cr[ií]tico|x\d+)\s*([^,)]*)", dano, flags=re.I)
            if cm and ("crít" in dano.lower() or "crit" in dano.lower() or "x" in dano.lower()):
                critico = cm.group(0).strip()
            ataques.append(
                {
                    "nome": nome_atq[:120],
                    "bonus_ataque": am.group(2),
                    "dano": dano[:80],
                    **({"critico": critico[:40]} if critico else {}),
                }
            )
    # fallback genérico
    if not ataques:
        for am in re.finditer(
            r"([A-Za-zÀ-ú][A-Za-zÀ-ú0-9'’\-]{2,30})\s+([+-]\d+)\s*\((\d*d\d[^)]*)\)",
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
    # dedup
    seen = set()
    atq_out = []
    for a in ataques:
        key = (a["nome"].lower(), a["bonus_ataque"])
        if key in seen:
            continue
        seen.add(key)
        atq_out.append(a)
    item["ataques"] = atq_out[:6]
    item["descricao_curta"] = (
        f"{item.get('tipo_criatura', 'Criatura')} {item.get('tamanho', '')}, "
        f"ND {item.get('nd_rotulo', item.get('nd'))}."
    ).strip()
    return item


def column_stream(page_text: str, side: str, mid: int = 52) -> str:
    lines: List[str] = []
    for ln in page_text.splitlines():
        if len(ln) <= mid:
            left, right = ln.rstrip(), ""
        else:
            left, right = ln[:mid].rstrip(), ln[mid:].rstrip()
        lines.append(left if side == "left" else right)
    return "\n".join(lines)


def enriquecer_com_blocos(
    skeleton: List[Dict[str, Any]], texto_blocos: str
) -> List[Dict[str, Any]]:
    """Localiza títulos no layout completo; extrai stats da coluna correspondente."""
    pages = texto_blocos.split("\x0c")
    found: Dict[str, Tuple[str, int]] = {}

    for i, page in enumerate(pages):
        pagina = (BLOCOS_PDF_INI + i) - PDF_OFFSET
        left = column_stream(page, "left")
        right = column_stream(page, "right")
        # Nomes mais longos primeiro (evitar «Esqueleto» capturar «Esqueleto de elite»)
        sk_sorted = sorted(skeleton, key=lambda s: len(s["nome"]), reverse=True)
        for sk in sk_sorted:
            if sk["slug"] in found:
                continue
            nome = sk["nome"]
            m = re.search(
                rf"{re.escape(nome)}\s+ND\s+(1/4|1/2|\d+)\b",
                page,
                flags=re.I,
            )
            if not m:
                continue
            # exigir limite de palavra no início do nome
            if m.start() > 0 and page[m.start() - 1].isalnum():
                continue
            line_start = page.rfind("\n", 0, m.start()) + 1
            col_pos = m.start() - line_start
            side = "left" if col_pos < 52 else "right"
            col_txt = left if side == "left" else right
            m2 = re.search(rf"(?<![A-Za-zÀ-ú]){re.escape(nome)}\b", col_txt, flags=re.I)
            if m2:
                window = col_txt[m2.start() : m2.start() + 2200]
            else:
                window = page[m.start() : m.start() + 2200]
            if not re.search(r"\bND\s+", window[:100], flags=re.I):
                window = f"{nome} ND {sk.get('nd_rotulo', sk.get('nd'))}\n{window}"
            found[sk["slug"]] = (window, pagina)

        # Título curto «Goblin ND» → goblin-salteador
        if "goblin-salteador" not in found:
            m = re.search(r"(?<![A-Za-zÀ-ú])Goblin\s+ND\s+(1/4|1/2|\d+)\b", page)
            if m:
                line_start = page.rfind("\n", 0, m.start()) + 1
                col_pos = m.start() - line_start
                side = "left" if col_pos < 52 else "right"
                col_txt = left if side == "left" else right
                m2 = re.search(r"(?<![A-Za-zÀ-ú])Goblin\b", col_txt)
                if m2:
                    found["goblin-salteador"] = (
                        col_txt[m2.start() : m2.start() + 2200],
                        pagina,
                    )

        m = re.search(r"Guerreiro\s*\n\s*de Chifres\s+ND\s+(\d+)", page, flags=re.I)
        if m and "guerreiro-de-chifres" not in found:
            m3 = re.search(r"Guerreiro\s*\n\s*de Chifres", left, flags=re.I)
            if m3:
                found["guerreiro-de-chifres"] = (
                    left[m3.start() : m3.start() + 2200],
                    pagina,
                )

    out: List[Dict[str, Any]] = []
    for sk in skeleton:
        if sk["slug"] in found:
            window, pagina = found[sk["slug"]]
            out.append(parse_stats_window(window, sk, pagina))
        else:
            nd = float(sk.get("nd") or 1)
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
                    "pv_max": max(1, int(8 + 6 * nd)),
                    "pa_max": 0,
                    "ca": max(10, int(10 + nd)),
                    "iniciativa": 0,
                    "deslocamento": "9m",
                    "fort_total": 0,
                    "ref_total": 0,
                    "von_total": 0,
                    "rd": "",
                    "ataques": [],
                    "pagina_referencia": sk.get("pagina_referencia") or "v1.3 p.285",
                }
            )
    out.sort(key=lambda r: (float(r.get("nd") or 999), str(r.get("nome") or "").lower()))

    # Funde stats do stub legado quando a entrada ficou sem ataques (ex.: Goblin salteador)
    stub_path = (
        Path(__file__).resolve().parent.parent
        / "backend/app/games/tormenta/data/bestiario_mb_stub.json"
    )
    if stub_path.is_file():
        try:
            stub_raw = json.loads(stub_path.read_text(encoding="utf-8"))
            stubs = {
                str(s.get("slug")): s
                for s in (stub_raw.get("criaturas") or [])
                if isinstance(s, dict) and s.get("slug")
            }
            for c in out:
                if c.get("ataques"):
                    continue
                for alias in c.get("aliases") or []:
                    st = stubs.get(str(alias))
                    if not st:
                        continue
                    for k in (
                        "for_valor",
                        "des_valor",
                        "con_valor",
                        "int_valor",
                        "sab_valor",
                        "car_valor",
                        "pv_max",
                        "ca",
                        "iniciativa",
                        "deslocamento",
                        "tamanho",
                        "fort_total",
                        "ref_total",
                        "von_total",
                        "rd",
                        "ataques",
                        "tipo_criatura",
                    ):
                        if st.get(k) is not None:
                            c[k] = st[k]
                    break
        except (OSError, json.JSONDecodeError, TypeError):
            pass
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    if not args.pdf.is_file():
        raise SystemExit(f"PDF não encontrado: {args.pdf}")

    skeleton = extrair_tabela_7_1(pdftotext_pages(args.pdf, TABELA_PDF, TABELA_PDF))
    texto_blocos = pdftotext_pages(args.pdf, BLOCOS_PDF_INI, BLOCOS_PDF_FIM)
    criaturas = enriquecer_com_blocos(skeleton, texto_blocos)

    payload = {
        "versao": 2,
        "fonte": "t20_v13",
        "nota": (
            "Metadados mecânicos + remissão; sem texto longo do livro. "
            "Extraído localmente do PDF v1.3 (Tabela 7-1 + blocos pp. 286–316)."
        ),
        "criaturas": criaturas,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    com_atq = sum(1 for c in criaturas if c.get("ataques"))
    print(f"OK: {len(criaturas)} criaturas ({com_atq} com ataques) → {args.out}")


if __name__ == "__main__":
    main()
